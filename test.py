#!/bin/python3
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

TESTS = [
    ("100b zeros", 
        zeros(100), [], 2**0,
        b'ceac9c2b81d3b7db21503b9b2615f4736dd2e3264c91a0d8b56eb525f92d4d20  -\n'),
    ("1K zeros", 
        zeros(1000), [], 2**0,
        b"c801d618c10d97d64d45a50505256e95862220d6796c8fdcd516d6720c8c4f67  -\n"),
    ("10K zeros",
        zeros(10000), [], 2**0,
        b"37fbff4fd69a82bd233db10ed5088b7bcaa71271a731fa5723c6dbc55ae9123a  -\n"),
    ("100K zeros",
        zeros(100000), [], 2**0,
        b'a69498e8084b398febb9f4939cb08d9c9a1ad60ae1543ea09a5b3f6f3177e7b1  -\n'),
    ("100b random",
        junk(100), [], 2**0,
        b'c72b36a7dfa20b4b5fb0a971c51af0fce99b51fb63ecb8836da2941c44729959  -\n'),
    ("1K random",
        junk(1000), [], 2**0,
        b'f241c6423b2b379815e064044ef4da30468c6ebce9d1d858496fd36e7da222f3  -\n'),
    ("10K random",
        junk(10000), [], 2**3,
        b'52e0d4c62c7b0ad61abfad3934dde2a6eea004345304a68eede13d1aa4f0d984  -\n'),
    ("50K random",
        junk(50000), [], 2**5,
        b'e6c67978627d840ecaf482b0c8ff4d20c271bf4c31f76b6d95f42fee1683223e  -\n'),
    ("1K zeros, self-check", 
        zeros(1000), ["--no-skip-checks"], 2**3,
        b"c801d618c10d97d64d45a50505256e95862220d6796c8fdcd516d6720c8c4f67  -\n"),
    ("1K random, self-check",
        junk(1000), ["--no-skip-checks"], 2**4,
        b'f241c6423b2b379815e064044ef4da30468c6ebce9d1d858496fd36e7da222f3  -\n'),
]

failures = 0
for name, input_bytes, options, time_limit, expected_output in TESTS:
    options = DEFAULT_ARGS + options
    qr_command = " ".join(["python", "qr-backup"] + options)
    command = "{} | sha256sum".format(qr_command)
    start = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, input=input_bytes)
    end = time.time()
    elapsed = end - start
    elapsed, power = math.ceil(elapsed), math.ceil(math.log(elapsed, 2))
    if result.stdout == expected_output:
        print("+", name, "{}s".format(elapsed))
    else:
        print("-", name)
        print("  command:", command)
        print("  result:", result.stdout, "!=", expected_output[:20])
        failures += 1
    if elapsed > time_limit:
        print("SLOW", name, "{}s, <2^{}".format(elapsed, power))
        failures += 1
    elif elapsed <= time_limit / 3:
        print("FAST", name, "{}s, <2^{}".format(elapsed, power))
        pass

sys.exit(1 if failures > 0 else 0)
