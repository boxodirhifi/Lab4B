# Lab 4B - Task 6: The export that refused the cloud
#
# Answers:
# 6.1 export_report only needs target to have write(data: bytes) -> int.
#     The isinstance check is gone - any object with write() works (duck
#     typing).
# 6.2 typing.Protocol describes that need: class Writable with
#     write(self, data: bytes) -> int. It is used as the type of target.
#     BytesIO, S3Upload and FakeTarget have no common parent - structural
#     typing, not inheritance.
# 6.3 See the tests - all three targets work.
# 6.4 Duck typing moves the error to the first call of write() at runtime.
#     Passing an object without write() fails only when export_report first
#     tries to write. mypy catches it before the program runs - it reports
#     "Argument 2 to export_report has incompatible type ...; expected
#     Writable". (Verified with mypy on a scratch file.)
import io
from typing import Protocol
import pytest


class Writable(Protocol):
    def write(self, data: bytes) -> int: ...
def export_report(rows: list[list[object]], target: Writable) -> None:
    for r in rows:
        target.write((",".join(map(str, r)) + "\n").encode())


class S3Upload:
    def __init__(self, bucket: str, key: str) -> None:
        self.bucket, self.key = bucket, key
        self.parts: list[bytes] = []

    def write(self, data: bytes) -> int:
        self.parts.append(data)
        return len(data)


class FakeTarget:
    """A tiny fake just for tests."""

    def __init__(self) -> None:
        self.chunks: list[bytes] = []

    def write(self, data: bytes) -> int:
        self.chunks.append(data)
        return len(data)


def test_target_without_write_fails_when_writing() -> None:
    class NoWrite:
        pass

    with pytest.raises(AttributeError):
        export_report([["name"]], NoWrite())  # type: ignore[arg-type]


ROWS: list[list[object]] = [["name", "qty"], ["apple", 3], ["pear", 5]]
EXPECTED = b"name,qty\napple,3\npear,5\n"


def test_export_to_bytesio() -> None:
    buf = io.BytesIO()
    export_report(ROWS, buf)
    assert buf.getvalue() == EXPECTED


def test_export_to_s3_upload() -> None:
    s3 = S3Upload("bucket", "report.csv")
    export_report(ROWS, s3)
    assert b"".join(s3.parts) == EXPECTED


def test_export_to_fake() -> None:
    fake = FakeTarget()
    export_report(ROWS, fake)
    assert b"".join(fake.chunks) == EXPECTED
