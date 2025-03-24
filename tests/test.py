#!/bin/python3
"""
These are tests for qr-backup.

Each test has three possible failure modes. In order of severity, they are
(1) Correctness: Restore test (incorrect-restore)
    If we back up a file, and then restore it, is the output the same as the
    original?
(2) Performance: Speed regression test (too-slow)
    Does the backup and restore work quickly enough?

    Note: too-fast can also be reported, which means you have improved the
          test speed, and need to update the "target" running time
(3) Reproducibility: Backup regression test (backup-regession)
    Is the output bitwise-identical to last time the tests were *blessed*
        blessed: marked correct by hand
"""

REPRODUCIBILITY_FAILING = """
This is the most basic reproducibility test, so something has changed.

Reproducibility (bitwise-identical output) is not actually a
requirement for qr-backup as long as restores continue to work across
versions. Rather, it's a first check. If there were no changes, a
human being doesn't even have to look.

For this reason, it's nice if we can make the output never change in
any way, because then we don't need human judgement.

Because of this nice property, you should default to considering it
worth fixing if reproducibilty tests fail (rather than rubber-stamping changes).

To narrow down what changed, compare the ouput of zeros.pdf (we just generated
it for you) with the file tests/regression.pdf (a known-good version).

My suggested process to get started:

1. 'git checkout' the last commit in which tests/regression.pdf was last
   touched, and re-generate a new version using

       dd if=/dev/zero count=1 bs=100 | python3 qr-backup - >regression2.pdf
   
   If the output is identical to regression.pdf, this confirms the change was
   in the qr-backup repository.

   Either way, proceed with the steps 2 and on.

   If the output is NOT identical, it's likely there was a change in some
   dependency, instead. For example, zbar, PIL, qrcode, reedsolo, tar,
   libz, etc.

   If possible, qr-backup would like to have reproducible output
   even in the face of library changes.

   Another possibility is differing output across runs.
   We once accidentally embedded the date in pdfs made during test runs.

2. Convert each of zeros.pdf and tests/regession.pdf to a png. Compare them
   using a visual diff tool online.

   Have the QR codes changed, the instructions, or neither?

   If neither, the PDF output phase is likely not reproducible.

3. If the textuual instructions changed this commit (and nothing else!)
   you can safely bless the new output.

   If something else changed too, split the commit in half.

4. If the QR codes have changed, what changed about the data inside?
   Use zbarimg to extract data from both PDFs and compare with 'diff'.

   If the data is the same, the QR output is likely not reproducible.

After carefully understanding why reproducibility has failed, and deciding
it's a good tradeoff and we can restore past backups, you can choose to
bless the new output.

The code to do this is printed at the bottom of the tests.

Once you bless output, make sure that tests pass! If output is
not consistent even between runs, this is a bug in qr-backup.
"""

import hashlib
import math
import random
import subprocess
import sys
import textwrap
import time

def zeros(length):
    return b'\0'*length
def junk(length):
    r = random.Random(1)
    return bytes(r.getrandbits(8) for _ in range(length))

RED = '\033[91m'
GREEN = '\033[92m'
ENDC = '\033[0m'
def print_red(x):
    print(RED + x + ENDC)
def print_green(x):
    print(GREEN + x + ENDC)

def program_present(program):
    """Return True or False depending on whether the program is found in the environment"""
    return subprocess.call(["which", program], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

DEFAULT_ARGS = ["--skip-checks", "-", "--backup-date", "2022-09-22"]
DEFAULT_RESTORE_ARGS = ["-"]

TESTS = [
    ("100b zeros",              zeros(100), [],                             2**0, [], 2**2),
    ("default options",         zeros(100), [
            "--dpi", "300",
            "--compress",
            "--erasure-coding",
            "--filename", "file",
            "--instructions", "page",
            "--num-copies 1",
            "--output", "-",
            "--page", "500", "600",
            "--qr-version", "10",
            "--scale", "5",
            "--shuffle",
                                             ],                             2**0, [], 2**2),
    ("--no-compress",           zeros(100), ["--no-compress"],              2**0, [], 2**2),
    ("--dpi",                   zeros(100), ["--dpi", "50"],                2**0, [], 2**3),
    ("--encrypt",               zeros(100), ["--encrypt", "PASSWORD"],      2**0, ["--encrypt", "PASSWORD"], 2**3),
    ("--encrypt-print-passphrase", zeros(100), ["--encrypt", "PASSWORD", "--encrypt-print-passphrase"], 2**0, ["--encrypt", "PASSWORD"], 2**3),
    ("--no-erasure-coding",     zeros(100), ["--no-erasure-coding"],        2**0, [], 2**3),
    ("--error-correction L",    zeros(100), ["--error-correction", "L"],    2**0, [], 2**2),
    ("--error-correction Q",    zeros(100), ["--error-correction", "Q"],    2**0, [], 2**2),
    ("--error-correction H",    zeros(100), ["--error-correction", "H"],    2**0, [], 2**2),
    ("--filename",              zeros(100), ["--filename", "TEST_FILENAME"],2**0, [], 2**2),
    ("--instructions both",     zeros(100), ["--instructions", "both"],     2**0, [], 2**3),
    ("--instructions cover",    zeros(100), ["--instructions", "cover"],    2**0, [], 2**3),
    ("--instructions none",     zeros(100), ["--instructions", "none"],     2**0, [], 2**2),
    ("--note (1)",              zeros(100), ["--note", "A"],                2**0, [], 2**2),
    ("--note (2)",              zeros(100), ["--note", "A", "--note", "B"], 2**0, [], 2**2),
    ("--num-copies",            zeros(100), ["--num-copies", "3"],          2**0, [], 2**2),
    ("--page",                  zeros(100), ["--page", "100", "200"],       2**0, [], 2**0),
    ("--qr-version",            zeros(100), ["--qr-version", "15"],         2**0, [], 2**2),
    ("--scale",                 zeros(100), ["--scale", "10"],              2**0, [], 2**2),
    ("--no-shuffle",            zeros(100), ["--no-shuffle"],               2**0, [], 2**2),
    ("1K zeros",                zeros(1000),[],                             2**0, [], 2**2),
    ("10K zeros",               zeros(10000), [],                           2**0, [], 2**2),
    ("100K zeros",              zeros(100000), [],                          2**0, [], 2**2),
    ("100b random",             junk(100),  [],                             2**0, [], 2**2),
    ("1K random",               junk(1000), [],                             2**0, [], 2**2),
    ("10K random",              junk(10000),[],                             2**3, [], 2**4),
    ("50K random",              junk(50000),[],                             2**5, [], 2**7),
    ("1K zeros, self-check",    zeros(1000),["--no-skip-checks"],           2**4, [], 2**2),
    ("1K random, self-check",   junk(1000), ["--no-skip-checks"],           2**4, [], 2**2),
]

BLESSED_OUTPUT = {
    # These two had better be the same!
    '100b zeros': 'ed26a865598955e799e310c3bb38549b68ea951a11af2ae9c3a887ab427e9288',
    'default options': 'ed26a865598955e799e310c3bb38549b68ea951a11af2ae9c3a887ab427e9288',

    # Options need to be checked by hand when updating
    '--encrypt': None, # Encryption is non-deterministic
    "--encrypt-print-passphrase": None,

    '--no-compress': 'af282809a01c4a163372f9237b07e36e779f039c383a9b324d149674b07cfb40',
    '--dpi': '0b9bab6921925979a3c4e88e59e51e6d63b5c0830a7c0ff77a7aad2475b4502c',

    '--no-erasure-coding': 'c0a08d86b71280517d1ff3cf56c7bbb998fdece72e3f996546877b1ca1df485e',
    '--error-correction L': 'b1043946459cb7367baa4214edd062671f6c78a6937e0287c7ca2f832ceacece',
    '--error-correction Q': 'a3efa49a970267cadb5d4dd3f0fcb67d69bc5069d51809f16754f06dc74de286',
    '--error-correction H': '2caa340d11e530a7e770caf71a3d0efee85defe4f5aec315b9c00bda6658089f',
    '--filename': '9a61e8185bfcf9b9c3d2901baea7430b448ed6e0e03759619045b61a38e29d4e',
    '--instructions both': '6ad4661009ebda82e6618f81caaa2fa43df1ac7d4a938ef3a7818588a8cc3c6b',
    '--instructions cover': '452f3e23a7f71e1f9d1892d64910ff185f12799dc5093f29f085fe003bd69629',
    '--instructions none': 'c66fdd3e1a7fd3107f95daab2d07b65cfe5e4b679fef5b2dca73d004baee494d',
    '--note (1)': '6cdf1ba777d47c68a92eb1f49f35b8bd186431e639d560b6f1bacee2a3ee03e3',
    '--note (2)': '8085233b46a4c61477fae0e9abea0c7f751f829763eaeaee36a3de3e6046ad9d',
    '--num-copies': '7c705557390d346eb87bb08ea437ed8a42198b2ceeea296fbf891c1b20c695e2',
    '--page': '8b3cfdb1e5b07ec72c552f6ab95ab39c04d419d23afad31b7b78fda395d435e9',
    '--qr-version': '1add32b1947948f32d6baab525a5621930a46cc2438012953b8992e930adea70',
    '--scale': '4cc28752038be68e69bd9b52ef3ab1aa310ce216be7af86e5cdfa0582c61e9b1',
    '--no-shuffle': '10559366e0b5590660838b5c7893f1a3fb22fefab39e943dc667cfc34c82d6c9',

    '1K zeros': '0f5da5bd812284e6a18f974af3187b442c4fed0cc595c231b96a5bdd4b0cd965',
    '10K zeros': '68328734a28dcc05d9884641c591f0592920f5efb861062a17877a0557400e0c',
    '100K zeros': 'b3fa3458bdf24863d1450d0c3b407c2b7f4847c2dc9d841b9a88c20e89f720b1',
    '100b random': '59512f3c17bdeb122b652c4fb130e4094f21159d965bea73847177ac51237417',
    '1K random': '7f9aeeea1ba41b6f6044bdeda64e87b626942dbead4ba409bc1a3f2195b91a2a',
    '10K random': '63222f94ba30f2e887deb0a85ab032d0fe5c6e87737552d5b151c0b0556888b0',
    '50K random': '4198a84b9a35f62108c26bd698295d1937d7257382e47db6f79ac8c8613a29a4',
    '1K zeros, self-check': '0f5da5bd812284e6a18f974af3187b442c4fed0cc595c231b96a5bdd4b0cd965',
    '1K random, self-check': '7f9aeeea1ba41b6f6044bdeda64e87b626942dbead4ba409bc1a3f2195b91a2a',
}


def do_test(test, new_blessed):
    name, input_bytes, options, time_limit, restore_options, restore_time_limit = test
    expected_sha = BLESSED_OUTPUT.get(name, b'')

    failures = 0

    options = DEFAULT_ARGS + options
    qr_command = " ".join(["python3", "qr-backup"] + options)
    start = time.time()
    result = subprocess.run(qr_command, shell=True, capture_output=True, input=input_bytes)
    elapsed = time.time() - start
    output_bytes = result.stdout
    sha = hashlib.sha256(output_bytes).hexdigest()
    elapsed, power = math.ceil(elapsed), math.ceil(math.log(elapsed, 2))

    # TODO: Check the data inside the QR-codes as a second, much-less-flaky regression suite.
    # Note that "regression" should really be called "reproducibility"

    if expected_sha is None: # Some tests are non-deterministic (ones using encryption)
        pass
    elif result.returncode != 0:
        print_red("failing-command {} {}s".format(name, elapsed))
        print_red(textwrap.indent(result2.stderr.decode("utf8"), "  "))
        failures += 1
        return failures, None
    elif sha == expected_sha:
        print_green("backup-no-regression {} {}s".format(name, elapsed))
    else:
        print_red("backup-regression {} {}s".format(name, elapsed))
        print("  command:", qr_command)
        print("  result:", sha, "!=", expected_sha)
        failures += 1

        if name == '100b zeros':
            print_red(REPRODUCIBILITY_FAILING)
            subprocess.run("dd if=/dev/zero count=1 bs=100 2>/dev/null | python3 qr-backup - >zeros.pdf", shell=True)

    if elapsed > time_limit*2:
        print_red("too-slow", name, "{}s, <2^{}".format(elapsed, power))
        failures += 1
    elif elapsed <= time_limit / 3:
        print("too-fast", name, "{}s, <2^{}".format(elapsed, power))
        pass

    restore_options = DEFAULT_RESTORE_ARGS + restore_options
    restore_command = " ".join(["python3", "qr-backup", "--restore"] + restore_options)
    start = time.time()
    result2 = subprocess.run(restore_command, shell=True, capture_output=True, input=output_bytes)
    elapsed = time.time() - start
    restored_bytes = result2.stdout
    elapsed, power = math.ceil(elapsed), math.ceil(math.log(elapsed, 2))

    if result2.returncode != 0:
        print_red("failing-command {} {}s".format(name, elapsed))
        print_red(textwrap.indent(result2.stderr.decode("utf8"), "  "))
        failures += 1
        return failures, None
    elif input_bytes == restored_bytes:
        print_green("correct-restore {} {}s".format(name, elapsed))
        if expected_sha is not None and sha != expected_sha:
            new_blessed[name] = sha   
    else:
        print_red("incorrect-restore {} {}s".format(name, elapsed))
        print("  command:", restore_command)
        #print(input_bytes, restored_bytes)
        failures += 1
    if elapsed > restore_time_limit*2:
        print_red("too-slow", name, "{}s, <2^{}".format(elapsed, power))
        failures += 1
    elif elapsed <= restore_time_limit / 3:
        print("too-fast", name, "{}s, <2^{}".format(elapsed, power))
        pass

    return failures, sha


if __name__ == "__main__":
    if not program_present("zbarimg"):
        print_red("To run tests, install the packages: zbar")
        sys.exit(6)

    failures = 0
    new_blessed = {}
    for test in TESTS:
        new_failures, sha = do_test(test, new_blessed)
        failures += new_failures
        if False and new_failures > 0:
            with open("failure.bin", "wb") as f:
                f.write(test[1])
            print("exit on first failure")
            break

    if len(new_blessed) > 0:
        print("NEW BLESSED_OUTPUT = {")
        for k, v in new_blessed.items():
            print("{}: {},".format(repr(k), repr(v)))
        print("}")

    print("{} failures".format(failures))
    if failures > 0:
        print_red(__doc__)
    sys.exit(1 if failures > 0 else 0)
