from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from inspect import isabstract
from pathlib import Path
from shutil import copy2
from typing import ClassVar, Optional, Self

from ..paths.build import BuildPaths
from ..projectv2.targets import Target
from ..utils.process import ProcessBuilder
from ..utils.string import assert_stringifyable_value
from ..utils.path import PathLike
from .base_run import BaseCommandRunner


@dataclass
class CMakeBuilder(BaseCommandRunner):
    path: str = field(default="cmake")

    build_dir: str = field(default=".")
    source_dir: str = field(default="..")

    build_type: str = field(default="MinSizeRel")
    generator: Optional[str] = field(default=None)
    install_prefix: str = field(default="/")
    toolchain_file: Optional[Path] = None

    args: dict[str, str] = field(default_factory=dict)

    def add_arg(self, k: str, v: str):
        self.args[k] = v

    def set_toolchain(self, paths: BuildPaths, target: Target):
        self.toolchain_file = paths.build_aux_dir / "cmake"
        self.toolchain_file /= f"{target.info.name2}.cmake"

    def build_process(self) -> ProcessBuilder:
        res = ProcessBuilder([self.path])
        res.env = self.env
        res.args.extend(["-S", self.source_dir])
        res.args.extend(["-B", self.build_dir])
        res.args.extend(["--install-prefix", self.install_prefix])
        if self.generator is not None:
            res.args.extend(["-G", self.generator])
        if self.toolchain_file is not None:
            res.args.extend(["--toolchain", str(self.toolchain_file)])
        #cmd.extend([
        #    #"-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON",
        #    "--log-level=VERBOSE",
        #    #"--debug-trycompile",
        #])
        args = {
            "CMAKE_BUILD_TYPE": self.build_type,
            #"CMAKE_INSTALL_PREFIX": self.install_prefix,
            #"CMAKE_STAGING_PREFIX": self.install_prefix,
            "BUILD_SHARED_LIBS": "OFF",
        }
        args.update(self.args)
        res.args.extend([
            f"-D{k}={v}"
            for k, v in args.items()
        ])
        return res

    def run(self):
        cmd = self.build_process()
        cmd.run()
