#!/bin/python3
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
    '100b zeros':      'c6308f52da054b6e9eb5ce02e5fced8889ac80fb45c0c2bd60c1522ddce8ba14',
    'default options': 'c6308f52da054b6e9eb5ce02e5fced8889ac80fb45c0c2bd60c1522ddce8ba14', # This had better be the same!

    # Options need to be checked by hand when updating
    '--no-compress': '1d8ec11472c4709fda63f3112a408db2da6c50a112dac8b0b4e0548cbea673f5',
    '--dpi': 'd363989549c855e96e0dda855756829c6b1f8f11b8ffe854b02cf6104466c072',
    # Encryption is non-deterministic
    '--encrypt': None,
    "--encrypt-print-passphrase": None,
    '--no-erasure-coding': '6746f3ca2b75d7397eda1e63fab1167b5a4cde44fabe681d7a48b1486ed39cb6',
    '--error-correction L': '8ab1475050ec7ebdd1d20ca46eb4a7083031922ebd1a573dba0ca80abb25f65a',
    '--error-correction Q': 'ec943a14a116ca596bc8f58f3fe006e461d68dce788ea9926a822d659df292dc',
    '--error-correction H': '1aad991555e4162d9610d8e989600da5e4031a8399a7082afb032e26e9891200',
    '--filename': '8137004c57a545e386cc0459a4ac802b949601f3a640c8fd859415652dc1b0d4',
    '--instructions both': '725cb6be5d80a6e76b0166fea3205daa61c3a2db5404f4f2802c5208f0a157d1',
    '--instructions cover': '4878036208da2bb5b02a0aadc9473756f3e8e3898e3540cef75ea0f0dd186c99',
    '--instructions none': 'ed80f71717140037506abe1d3aea05d97278d64d97b906abfa6d9ff85286fe33',
    '--note (1)': 'cf904a8e4d87e3135ca81ce79c0e93dbdc4cb2775224426f99c27be5f5a18d78',
    '--note (2)': 'ed9100f706bff9984d11fc6a845074c47b721856484c87344c7cabfc1e1a2c83',
    '--num-copies': '19b89f0c9a770052b8ccdc00597056375306ae8e0278373bfd112406ff188f2e',
    '--page': '0696073fe4d8c5c4d1bda3f52036952860dc033abfd5ab002dbcde037b27d0c4',
    '--qr-version': '36f0ce65559ab37779a022c2492dbf1d029912fb9e740e92db053ee60ab6a1ed',
    '--scale': '3bda1a470226c115a0f3ad85f47748b71d40a1183c65e79ef29afa876bb86bc3',
    '--no-shuffle': 'ddbf172b473df1856a5015423446b4626f3dfdcaa644f290a4f84b06a5acb2a9',

    '1K zeros': 'd45df72505b649c41f6fb4a6aae31de1b6d6ee57f6d98141554bda186457b9b6',
    '10K zeros': 'ad3c0e8eccaedc88786b51b168573c6bf952f923766e6875e1579050d070516f',
    '100K zeros': 'bcefefc7441bcc341f4e2cda9a9f7f74b59bfa22b7a99bef4e6561999e465f66',
    '100b random': 'ce704c5e984ac7b54a78e5da19d69a02e3ffa505d3ae0733759433108f599fca',
    '1K random': '0541b29b91950263b3f0ff5936b1c994b3b576658257d79d7c49fa750a417619',
    '10K random': '9728f552c43d02d7a609528af78b84279152fcbeee0b06272d69b504a57ed037',
    '50K random': '93fcea86604b53e2c91e668303ef6a58c11a0782398171bb41c5a16370034015',
    '1K zeros, self-check': 'd45df72505b649c41f6fb4a6aae31de1b6d6ee57f6d98141554bda186457b9b6',
    '1K random, self-check': '0541b29b91950263b3f0ff5936b1c994b3b576658257d79d7c49fa750a417619',
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
        print_green("+b {} {}s".format(name, elapsed))
    else:
        print_red("-b {} {}s".format(name, elapsed))
        print("  command:", qr_command)
        print("  result:", sha, "!=", expected_sha)
        failures += 1
        failed = True
    if elapsed > time_limit*2:
        print_red("slow-b", name, "{}s, <2^{}".format(elapsed, power))
        failures += 1
        failed = True
    elif elapsed <= time_limit / 3:
        print("fast-b", name, "{}s, <2^{}".format(elapsed, power))
        pass

    restore_options = DEFAULT_RESTORE_ARGS + restore_options
    restore_command = " ".join(["python3", "qr-backup", "--restore"] + restore_options)
    start = time.time()
    result2 = subprocess.run(restore_command, shell=True, capture_output=True, input=output_bytes)
    elapsed = time.time() - start
    restored_bytes = result2.stdout
    elapsed, power = math.ceil(elapsed), math.ceil(math.log(elapsed, 2))

    if input_bytes == restored_bytes:
        print_green("+r {} {}s".format(name, elapsed))
        if expected_sha is not None and sha != expected_sha:
            new_blessed[name] = sha   
    else:
        print_red("-r {} {}s".format(name, elapsed))
        print("  command:", restore_command)
        #print(input_bytes, restored_bytes)
        failures += 1
    if elapsed > restore_time_limit*2:
        print_red("slow-r", name, "{}s, <2^{}".format(elapsed, power))
        failures += 1
    elif elapsed <= restore_time_limit / 3:
        print("fast-r", name, "{}s, <2^{}".format(elapsed, power))
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
