#!/bin/python3
"""
These are tests for qr-backup.

Each test has three possible failure modes. In order of severity, they are
(1) Correctness: Restore test (-r)
    If we back up a file, and then restore it, is the output the same as the
    original?
(2) Performance: Speed regression test (-r-slow)
    Does the backup and restore work quickly enough?
(3) Reproducibility: Backup regression test (-b)
    Is the output bitwise-identical to last time the tests were *blessed*
        blessed: marked correct by hand
"""
import hashlib
import math
import random
import subprocess
import sys
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
    '100b zeros':      '62e9ba9561c5f7d55e6005b49b134b3db25834aca900f1d4b1f8860083d1c851',
    'default options': '62e9ba9561c5f7d55e6005b49b134b3db25834aca900f1d4b1f8860083d1c851', # This had better be the same!

    # Options need to be checked by hand when updating
    '--no-compress': 'f91656ae53d79aca5bbf018ec2c0cbe4d1b4ae37d26204103425932647f1b16b',
    '--dpi': '2de57135237467259b04c20af969211ae853c8ff1e99ad22e0c38fc0f1cea29d',
    # Encryption is non-deterministic
    '--encrypt': None,
    "--encrypt-print-passphrase": None,
    '--no-erasure-coding': '0406a41cc0f9b39a205152c95543f05b0b141ef3ca6981fb4b7be44dc0a87537',
    '--error-correction L': 'bbbd60bafb23fdd17ce6625e321cdc8a97843fc1b7c0256000ee9381f5ab8552',
    '--error-correction Q': '2387a6b5ff3d1f4b7c93f399fcf8778798c547e968e7ebb558c6d1a4c42df854',
    '--error-correction H': '0cac40521b96fecc0631509bf0463270c05db8e3e2fb31995de2785e14c6e090',
    '--filename': '6833abc92c168a266ebbd144400ce7eb1c2f6162722dcfd51f896cbeef471cb5',
    '--instructions both': '5abcab841702e7ea4f5804b564d4e7ce4e84e6ae9e40665abfb394a450632226',
    '--instructions cover': '0793f628f6ae2dd4c4bf5653af6f3a78f292979721a14b5c2ac5a35351b9795e',
    '--instructions none': '69ace79dd3799a69f824c11e5423e303d09e2d47affc628532429cc1979eed6e',
    '--note (1)': '2b8ef3cefebcb4395362661aed62518a312001b835f0b8a8d29eb1c03240fd08',
    '--note (2)': '835a474a2bbff740e2c4671415cb980e668d26b505e1daf656384acf18a5c51b',
    '--num-copies': 'e2b6e7e5c711887d213822b385a9f0d7cb63e23fb17a1861131410ff785a5df1',
    '--page': '5aee0cb5a8b50bf1b41be9ee14ee263a4ad68b181c022751acc5c56247c2b8a1',
    '--qr-version': '42aa1dee32c7c74ac3a059f748ed2e38af8d9546ebea35adc4edabc642a4559f',
    '--scale': '0587bc699f3e483e1d712009d779faf888813ce857ca4bb0ce86548ec131d655',
    '--no-shuffle': 'ab3997517850c665db39cffde95088f6d2e7bcce99f6f7fe2bdc1febacfc9690',
    '1K zeros': '72acaeb01130fc72cc9daad380ce4b1d8e88f3d45a5ac5a76c2917a36cecb211',

    '10K zeros': '14ed149a161ec19e8b4353a9c16c7f29805143ac75cb5b0a891e031166940f6b',
    '100K zeros': '78e96dceabcaa4d07da3a21952d45f2235ffb9480000a6a62fc45bada939b3ae',
    '100b random': 'c1773a62db5bda8e7600d7b99b7a69ad245692717d8519c966230f048b306333',
    '1K random': '52fa6707761faae6a16bb0e16bcf32b94e8a895afc96ee354b6b32007227d19f',
    '10K random': '3cc61fc17f4ad2b9419133fdf94690c4f022ceb63e837e51fe61bb184644053f',
    '50K random': 'e196458408552a49a5fea40d23edf610354fcb5c87863f0dbff849066ecf8118',
    '1K zeros, self-check': '72acaeb01130fc72cc9daad380ce4b1d8e88f3d45a5ac5a76c2917a36cecb211',
    '1K random, self-check': '52fa6707761faae6a16bb0e16bcf32b94e8a895afc96ee354b6b32007227d19f',
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

    if expected_sha is None: # Some tests are non-deterministic (ones using encryption)
        pass
    elif sha == expected_sha:
        print_green("backup-no-regression {} {}s".format(name, elapsed))
    else:
        print_red("backup-regression {} {}s".format(name, elapsed))
        print("  command:", qr_command)
        print("  result:", sha, "!=", expected_sha)
        failures += 1
        failed = True
    if elapsed > time_limit*2:
        print_red("too-slow", name, "{}s, <2^{}".format(elapsed, power))
        failures += 1
        failed = True
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

    if input_bytes == restored_bytes:
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
    sys.exit(1 if failures > 0 else 0)
