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

import functools
import hashlib
import math
import random
import subprocess
import sys
import textwrap
import time

only_once = functools.cache # As long as it's called on a no-argument function :)

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
    # If you ever bless a new version, make sure to overwrite tests/regression.pdf with zeros.pdf
    '100b zeros': '4d2cd56bc5a890f2a87419ceec58d29cf9b576b14020ebbdabdd75597827add7',
    'default options': '4d2cd56bc5a890f2a87419ceec58d29cf9b576b14020ebbdabdd75597827add7',

    # Options need to be checked by hand when updating
    '--encrypt': None, # Encryption is non-deterministic
    "--encrypt-print-passphrase": None,

    '--no-compress': 'f4aaa755da4d6b84ff30da1880f40d83171f97b7531b1915afbd7554867f48b3',
    '--dpi': '22e15a09b519d543c209286636c6faf52c5fc800bab611487d4a47a2a477160b',

    '--no-erasure-coding': '923ca0be469692222a68d658440da5a7f48fd85c20610494a00048d4f0dcf755',
    '--error-correction L': 'f4dcbfe447b165b95735a5bd3a3ba3e0e5f9d2d7d9faddc362bf7a19a6b7bad4',
    '--error-correction Q': 'd9534c44c92f1e0ee1c019deb4b47e86df2f1ec29327adcfb2315f16c46d5b23',
    '--error-correction H': 'b276d2dce25fbfd2506fc4eeccb8a1d38e1e9017b1742cab855e3effc851235f',
    '--filename': '9a075dd3429141c9577c3eb6f3db379cd2e900ee5ca5bee5b9cc9e2e832774f2',
    '--instructions both': '4bb9f4ff23b9c1889ab84c4714a126524b9b811f4933b05fd20d01967dab9340',
    '--instructions cover': '4757a096d77b5c1cc0774f69577d1365d35d3113115901bbddf63d61411c3ed9',
    '--instructions none': '361e065a0addbe02a11385a8bb9510940e6d09cae6f0482223ca2f08013a1d00',
    '--note (1)': '49191147dbbe7d9a411567b54f74f86b235f387c8c4a28fe68dbcb86dc310fca',
    '--note (2)': '1dee193b34d777aa2a20097e3e800f2b4206d73e908168a338baa8011f9b23d6',
    '--num-copies': 'ba5f2936cfe981ffb5fa074f0893f084747527b00b313f0d86a29260b4f02f07',
    '--page': '551cfb9c092bd3c837f0cbf7fb14c7321dfcf5f0d7cb9d12a79e363004be4ce4',
    '--qr-version': 'eebf76bd76f62d6d0f097417ae8fd95cb10963c5dc71e68d88740420899a3325',
    '--scale': '7c402f001634271bdd04e58b7ebd5bbb71b3d249bc378efa4f5f57bb6d26d8de',
    '--no-shuffle': '8ce2b34dc9a57a3fb521bd59ba1f0ec1a7d51f8b67c54fc7ad21eec87454fe0f',
    '1K zeros': 'c952b0a40d1fa655b367b274672e0a9b1d56fc034fc690230a0ad842bc4eef53',
    '10K zeros': '1889f9ad99d9d7df224e3e65283d14602a62b14253bb1adff3c99ae38bc9734b',
    '100K zeros': '1ddfe806cd82e74c5d5f025aae2ce9f38577c9d9d2347337a75fe274e9477e2b',
    '100b random': 'c3f49775b97342e5e4fec58bdb34a3db21e0ee2afbc243d943df2bdc9c9b16df',
    '1K random': '0b330dbdabb7f987cff35d262d2e8512506eff5ae010b9c9918251de26f5d633',
    '10K random': '1c0b1d2b2e8f2a9cebdd29f37e05a8ead7bfd70e5eca9c91b368625742a66d51',
    '50K random': '3042edf630420c2aa0f95b0de9616ceaef0aece39e8773bcdfd163286afab7fe',
    '1K zeros, self-check': 'c952b0a40d1fa655b367b274672e0a9b1d56fc034fc690230a0ad842bc4eef53',
    '1K random, self-check': '0b330dbdabb7f987cff35d262d2e8512506eff5ae010b9c9918251de26f5d633',
}

@only_once
def make_pdf():
    print_red(REPRODUCIBILITY_FAILING)
    # Make a new regression.pdf for future generations
    qr_command = " ".join(["python3", "qr-backup"] + DEFAULT_ARGS) + " >zeros.pdf"
    subprocess.run(qr_command, shell=True, input=zeros(100))

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

    # TODO: "regression" should be called "reproducibility"

    # TODO: Check the data inside the QR-codes as a second, much-less-flaky regression suite.

    # TODO: Check the text inside the PDFs in a yet third, much-less-flaky regression suite.

    if expected_sha is None: # Some tests are non-deterministic (ones using encryption)
        pass
    elif result.returncode != 0:
        print_red("failing-command {} {}s".format(name, elapsed))
        print_red(textwrap.indent(result.stderr.decode("utf8"), "  "))
        failures += 1
        return failures, None
    elif sha == expected_sha:
        print_green("backup-no-regression {} {}s".format(name, elapsed))
    else:
        print_red("backup-regression {} {}s".format(name, elapsed))
        print("  command:", qr_command)
        print("  result:", sha, "!=", expected_sha)
        failures += 1

        if expected_sha == BLESSED_OUTPUT['100b zeros']:
            make_pdf()

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
        print_red("too-slow {} {}s, <2^{}".format(name, elapsed, power))
        failures += 1
    elif elapsed <= restore_time_limit / 3:
        print("too-fast {} {}s, <2^{}".format(name, elapsed, power))
        pass

    return failures, sha

def run_assertion_test(name, f):
    try:
        f()
        print_green(name)
        return 0
    except AssertionError as e:
        print_red(name)
        print("  {}".format(e))
        return 1
    except Exception as e:
        print_red(name)
        print_red("  test failed to run")
        print("  {}".format(e))
        return 1

def test_assert_reproducibile_current():
    out = subprocess.check_output(["sha256sum", "tests/regression.pdf"])
    expected = "{}  tests/regression.pdf\n".format(BLESSED_OUTPUT['100b zeros']).encode("UTF8")
    assert out == expected, "tests/regression.pdf does not match the expected SHA256 for the '100b zeros' test"

if __name__ == "__main__":
    if not program_present("zbarimg"):
        print_red("To run tests, install the packages: zbar")
        sys.exit(6)

    failures = 0
    new_blessed = {}

    # Additional, other tests that are not backup examples
    for name, f in {(k,v) for k,v in globals().items() if k.startswith("test_assert")}:
        failures += run_assertion_test(name, f)

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
