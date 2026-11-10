"""Corrupt length prefixes must fail cleanly, not with a raw ValueError."""

import base64
import importlib.machinery
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "qr-backup"
LOADER = importlib.machinery.SourceFileLoader("qr_backup_under_test", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(MODULE)


def test_length_roundtrip():
    encoded, _ = MODULE.length_encode(b"hello world")
    assert MODULE.length_decode(encoded) == b"hello world"


@pytest.mark.parametrize(
    "data",
    (
        b"noseparator",
        b"",
        b"abc rest",
        b"12x34 rest",
        b"-5 hello",
    ),
)
def test_length_decode_rejects_bad_prefix(data):
    with pytest.raises(ValueError, match="invalid length prefix"):
        MODULE.length_decode(data)


def _single_code(content):
    chunk = base64.b64encode(content)
    return {b"N1": chunk}, {b"N": 1, b"P": None}


def test_do_restore_roundtrip():
    payload, _ = MODULE.length_encode(b"hello world")
    codes, totals = _single_code(payload)
    assert (
        MODULE.do_restore(
            codes,
            totals,
            use_erasure=False,
            use_compression=False,
            use_encryption=False,
            encryption_passphrase=None,
        )
        == b"hello world"
    )


def test_do_restore_corrupt_content_exits_4():
    codes, totals = _single_code(b"noseparator")
    with pytest.raises(SystemExit) as exc:
        MODULE.do_restore(
            codes,
            totals,
            use_erasure=False,
            use_compression=False,
            use_encryption=False,
            encryption_passphrase=None,
        )
    assert exc.value.code == 4
