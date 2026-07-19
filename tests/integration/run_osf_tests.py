"""Fetch, verify, and run tests against the full tutorial dataset."""

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
from urllib.request import urlopen

URL = "https://osf.io/2a4kh/download"
SHA256 = "2c734d8991c03f9da6af874ac8fa9a8cfb43f5d7134637eedf04d528d48b3d65"
REPOSITORY = Path(__file__).resolve().parents[2]
CACHE_DIR = REPOSITORY / ".test-cache"
ARCHIVE = CACHE_DIR / "wnutils_tutorial_data.tar.gz"


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download():
    CACHE_DIR.mkdir(exist_ok=True)
    temporary_archive = ARCHIVE.with_suffix(".tmp")
    try:
        with (
            urlopen(URL, timeout=60) as response,
            temporary_archive.open("wb") as output,
        ):
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
        if checksum(temporary_archive) != SHA256:
            raise RuntimeError(
                "Downloaded OSF archive has an invalid checksum"
            )
        temporary_archive.replace(ARCHIVE)
    finally:
        temporary_archive.unlink(missing_ok=True)


def ensure_archive():
    if not ARCHIVE.exists() or checksum(ARCHIVE) != SHA256:
        print(
            "Downloading the wnutils tutorial test data from OSF...",
            flush=True,
        )
        download()
    else:
        print(f"Using cached tutorial test data: {ARCHIVE}", flush=True)


def extract(destination):
    destination = destination.resolve()
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        for member in archive.getmembers():
            if member.issym() or member.islnk():
                raise RuntimeError(
                    f"Archive link is not allowed: {member.name}"
                )
            member_path = (destination / member.name).resolve()
            if (
                destination not in member_path.parents
                and member_path != destination
            ):
                raise RuntimeError(f"Unsafe archive member: {member.name}")
        if sys.version_info >= (3, 12):
            archive.extractall(destination, filter="data")
        else:
            archive.extractall(destination)


def main():
    ensure_archive()
    with tempfile.TemporaryDirectory(prefix="wnutils-tutorial-") as temp_dir:
        data_dir = Path(temp_dir)
        extract(data_dir)
        environment = os.environ.copy()
        environment["WNUTILS_TUTORIAL_DATA"] = str(data_dir)
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-v",
                "tests/integration/test_tutorial_data.py",
            ],
            cwd=REPOSITORY,
            env=environment,
            check=True,
        )


if __name__ == "__main__":
    main()
