from shutil import copy2
from typing import Optional

from ...project.targets import Target
from ...utils.process import ProcessBuilder


def strip_bin(
    target: Target,
    binary: str,
    cmdname: Optional[str] = None,
    strip_all: bool = True,
):
    if cmdname is None:
        cmdname = target.info.get_cross() + "strip"
    cmd = ProcessBuilder([cmdname])
    if strip_all:
        cmd.args.append("--strip-all")
    cmd.args.append("--")
    cmd.args.append(binary)
    cmd.run()


def strip_bin_copy(
    target: Target,
    source: str,
    dest: str,
    cmdname: Optional[str] = None,
    strip_all: bool = True,
):
    copy2(source, dest)
    strip_bin(target, dest, cmdname, strip_all)
