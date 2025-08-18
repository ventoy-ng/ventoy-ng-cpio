import re
import tarfile
from hashlib import sha256
from io import BytesIO
from os import chdir, makedirs
from pathlib import Path
from typing import Optional
from urllib.request import urlopen

from zstd import ZSTD_uncompress

from ..paths.build import BuildPaths
from ..projectv2.project import Project
from ..schemas.sources import SourceInfo

TAR_REGEX = r"^(.*)\.(tar(\.[^\.]+)?|tgz)$"
TAR_REGEX_C = re.compile(TAR_REGEX)


def is_archive_file(filename: str) -> bool:
    regs = [
        TAR_REGEX_C,
    ]
    return any([
        reg.match(filename) is not None
        for reg in regs
    ])


def download_source(url: str) -> bytes:
    with urlopen(url) as req:
        data = req.read()
    assert isinstance(data, bytes)
    return data


def verify_source(this: SourceInfo, data: bytes):
    xhash = this.xhash
    assert xhash is not None
    sxhash = xhash.split(":")
    hash_kind = sxhash[0]
    assert hash_kind == "sha256"
    valid_hash_value = sxhash[1]
    hash_value = sha256(data)
    if hash_value.hexdigest() != valid_hash_value:
        raise ValueError


def extract_source_tar_builtin(
    paths: BuildPaths,
    data: bytes,
):
    stream = BytesIO(data)
    tmp_dir = paths.sources_dir
    makedirs(tmp_dir, exist_ok=True)
    old_dir = Path.cwd()
    with tarfile.open(mode="r:*", fileobj=stream) as file:
        chdir(tmp_dir)
        file.extractall()
        chdir(old_dir)


def extract_source_tar_any(
    paths: BuildPaths,
    data: bytes,
    extension: str,
):
    if extension == "zst":
        data = ZSTD_uncompress(data)
    elif extension in ["bz2", "gz", "xz", "tgz"]:
        pass
    else:
        raise NotImplementedError
    extract_source_tar_builtin(paths, data)


def extract_source_archive(
    paths: BuildPaths,
    filename: str,
    target_file: Path,
    data: Optional[bytes],
):
    if data is None:
        with target_file.open("rb") as file:
            data = file.read()
    exts = filename.split(".")
    ext0 = exts.pop()
    ext1 = exts.pop()
    if ext1 == "tar" or ext0 == "tar" or ext0 == "tgz":
        extract_source_tar_any(paths, data, ext0)
        return
    raise NotImplementedError


def handle_source_url(
    this: SourceInfo,
    target_file: Path,
    url: str,
    download_dir: Path,
):
    if target_file.exists():
        print("  Skipping download")
        return None
    makedirs(download_dir, exist_ok=True)
    print("  Downloading...")
    data = download_source(url)
    if this.xhash is not None:
        print("  Verifying...")
        verify_source(this, data)
    with target_file.open("wb") as file:
        file.write(data)
    print("  Done!")
    return data


def handle_source_archive(
    this: SourceInfo,
    paths: BuildPaths,
    filename: str,
    target_file: Path,
    data: Optional[bytes],
):
    extracted_name = this.get_extracted_name()
    extracted_path = paths.sources_dir / extracted_name
    if extracted_path.exists():
        print("  Skipping extracting")
        return
    print("  Extracting...")
    extract_source_archive(paths, filename, target_file, data)
    print("  Done!")


def prepare_source(this: SourceInfo, paths: BuildPaths):
    url = this.get_url()
    assert url is not None
    filename = this.get_filename()
    is_archive = is_archive_file(filename)
    print(repr(filename))
    download_dir = paths.sources_dir
    if is_archive:
        download_dir = paths.archives_dir
    else:
        # assumed: is a singular c file
        download_dir /= this.name
    target_file = download_dir / filename
    data = handle_source_url(this, target_file, url, download_dir)
    if is_archive:
        handle_source_archive(this, paths, filename, target_file, data)


def do_prepare(project: Project):
    for source in project.sources.values():
        if source.url is None:
            raise NotImplementedError
        prepare_source(source, project.get_build_paths())
