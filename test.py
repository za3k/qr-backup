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

DEFAULT_ARGS = ["--skip-checks", "-"]
DEFAULT_RESTORE_ARGS = ["-"]

TESTS = [
    ("100b zeros", 
        zeros(100), [], 2**0,
        'ceac9c2b81d3b7db21503b9b2615f4736dd2e3264c91a0d8b56eb525f92d4d20',
        [], 2**2),
    ("1K zeros", 
        zeros(1000), [], 2**0,
        "c801d618c10d97d64d45a50505256e95862220d6796c8fdcd516d6720c8c4f67",
        [], 2**2),
    ("10K zeros",
        zeros(10000), [], 2**0,
        "37fbff4fd69a82bd233db10ed5088b7bcaa71271a731fa5723c6dbc55ae9123a",
        [], 2**2),
    ("100K zeros",
        zeros(100000), [], 2**0,
        'a69498e8084b398febb9f4939cb08d9c9a1ad60ae1543ea09a5b3f6f3177e7b1',
        [], 2**2),
    ("100b random",
        junk(100), [], 2**0,
        'c72b36a7dfa20b4b5fb0a971c51af0fce99b51fb63ecb8836da2941c44729959',
        [], 2**2),
    ("1K random",
        junk(1000), [], 2**0,
        'f241c6423b2b379815e064044ef4da30468c6ebce9d1d858496fd36e7da222f3',
        [], 2**2),
    ("10K random",
        junk(10000), [], 2**3,
        '52e0d4c62c7b0ad61abfad3934dde2a6eea004345304a68eede13d1aa4f0d984',
        [], 2**4),
        # Known failure. Blame it on zbarimg
    ("50K random",
        junk(50000), [], 2**5,
        'e6c67978627d840ecaf482b0c8ff4d20c271bf4c31f76b6d95f42fee1683223e',
        [], 2**7),
    ("1K zeros, self-check", 
        zeros(1000), ["--no-skip-checks"], 2**4,
        "c801d618c10d97d64d45a50505256e95862220d6796c8fdcd516d6720c8c4f67",
        [], 2**2),
    ("1K random, self-check",
        junk(1000), ["--no-skip-checks"], 2**4,
        'f241c6423b2b379815e064044ef4da30468c6ebce9d1d858496fd36e7da222f3',
        [], 2**2),
]

failures = 0
for name, input_bytes, options, time_limit, expected_sha, restore_options, restore_time_limit in TESTS:
    failed = False

    options = DEFAULT_ARGS + options
    qr_command = " ".join(["python3", "qr-backup"] + options)
    start = time.time()
    result = subprocess.run(qr_command, shell=True, capture_output=True, input=input_bytes)
    elapsed = time.time() - start
    output_bytes = result.stdout
    sha = hashlib.sha256(output_bytes).hexdigest()
    elapsed, power = math.ceil(elapsed), math.ceil(math.log(elapsed, 2))

    if sha == expected_sha:
        print("+b", name, "{}s".format(elapsed))
    else:
        print("-b", name)
        print("  command:", command)
        print("  result:", sha, "!=", expected_sha)
        failures += 1
        failed = True
    if elapsed > time_limit:
        print("slow-b", name, "{}s, <2^{}".format(elapsed, power))
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
        print("+r", name, "{}s".format(elapsed))
    else:
        print("-r", name)
        print("  command:", restore_command)
        #print(input_bytes, restored_bytes)
        failures += 1
        failed = True
    if elapsed > restore_time_limit:
        print("slow-r", name, "{}s, <2^{}".format(elapsed, power))
        failures += 1
        failed = True
    elif elapsed <= restore_time_limit / 3:
        print("fast-r", name, "{}s, <2^{}".format(elapsed, power))
        pass

    if failed:
        with open("failure.bin", "wb") as f:
            f.write(input_bytes)
        sys.exit(1)

sys.exit(1 if failures > 0 else 0)
