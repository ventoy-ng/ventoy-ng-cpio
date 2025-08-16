from shutil import copy2
from typing import Optional

from ..projectv2.targets import Target
from ..utils.process import ProcessBuilder


def strip_bin(
    target: Target,
    bin: str,
    cmdname: Optional[str] = None,
    strip_all: bool = True,
):
    if cmdname is None:
        cmdname = target.info.get_cross() + "strip"
    cmd = ProcessBuilder([cmdname])
    if strip_all:
        cmd.args.append("--strip-all")
    cmd.args.append("--")
    cmd.args.append(bin)
    cmd.run()


def strip_bin_copy(
    target: Target,
    bin: str,
    starg: str,
    cmdname: Optional[str] = None,
    strip_all: bool = True,
):
    copy2(bin, starg)
    strip_bin(target, starg, cmdname, strip_all)
