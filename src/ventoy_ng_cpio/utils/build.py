from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from inspect import isabstract
from os import cpu_count, environ
from pathlib import Path
from shutil import copy2
from typing import ClassVar, Optional, Self

from ventoy_ng_cpio.paths.build import BuildPaths

from ..projectv2.targets import Target
from ..utils.process import ProcessBuilder
from .path import PathLike


def assert_stringifyable_value(v: object) -> bool:
    if v.__str__ != object.__str__:
        return True
    raise ValueError("Not stringifyable value: {}".format(
        v.__class__.__name__
    ))


def default_configure_name() -> Path:
    return Path("./configure")


@dataclass
class BaseCommandRunner(ABC):
    path: str
    cwd: Optional[Path] = field(default=None)
    env: dict[str, str] = field(default_factory=lambda: dict(environ))

    #@abstractmethod
    #def process_build(self) -> ProcessBuilder:
    #    raise NotImplementedError

    def _build_process_a(
        self,
    ) -> ProcessBuilder:
        res = ProcessBuilder([self.path])
        if self.cwd is not None:
            res.cwd = self.cwd
        res.env = self.env
        return res


@dataclass
class MakeLikeRunner(BaseCommandRunner, ABC):
    file: Optional[str] = field(default=None)

    def _build_process_b(
        self,
    ) -> ProcessBuilder:
        res = super()._build_process_a()
        if self.file is not None:
            res.args.extend(["-f", self.file])
        return res


class MakeStatus(Enum):
    Done = 0
    UpToDate = auto()
    #Failed = auto()

    def is_up_to_date(self) -> bool:
        return self == self.__class__.UpToDate


@dataclass
class MakeRunner(MakeLikeRunner):
    path: str = field(default="make")
    jobs: Optional[int] = field(default_factory=cpu_count)
    envs_strict: dict[str, str] = field(default_factory=dict)

    def build_process(
        self,
        targets: Optional[list[str]] = None,
    ) -> ProcessBuilder:
        res = super()._build_process_b()
        if self.jobs is not None:
            res.args.extend(["-O", "-j", str(self.jobs)])
        if self.envs_strict:
            res.args.extend([
                f"{k}={v}"
                for k, v in self.envs_strict.items()
            ])
        if targets:
            res.args.append("--")
            res.args.extend(targets)
        return res

    def run(
        self,
        targets: Optional[list[str]] = None,
    ):
        cmd = self.build_process(targets)
        cmd.run()

    def run_if_needed(
        self,
        targets: Optional[list[str]] = None,
    ):
        cmd = self.build_process(targets)
        cmd_check = cmd.copy()
        cmd_check.args.insert(1, "-q")
        if cmd_check.spawn().wait() == 0:
            return MakeStatus.UpToDate
        cmd.run()
        return MakeStatus.Done


@dataclass
class NinjaRunner(MakeLikeRunner):
    path: str = field(default="ninja")

    def build_process(
        self,
        targets: Optional[list[str]] = None,
    ) -> ProcessBuilder:
        res = super()._build_process_b()
        res.args.append("--verbose")
        if targets:
            res.args.append("--")
            res.args.extend(targets)
        return res

    def run(
        self,
        targets: Optional[list[str]] = None,
    ):
        cmd = self.build_process(targets)
        cmd.run()

    def run_if_needed(
        self,
        targets: Optional[list[str]] = None,
    ):
        cmd = self.build_process(targets)
        cmd_check = cmd.copy()
        cmd_check.args.insert(1, "--quiet")
        if cmd_check.spawn().wait() == 0:
            return MakeStatus.UpToDate
        cmd.run()
        return MakeStatus.Done


@dataclass
class ConfigureScriptWrapper(BaseCommandRunner):
    path: str = field(default="./configure")
    args: list[str] = field(default_factory=list)
    confenv: dict[str, str] = field(default_factory=dict)

    @classmethod
    def new(cls, path: PathLike) -> Self:
        return cls(str(path))

    def add_arguments(self, *args: object):
        self.args.extend([
            str(arg)
            for arg in args
            if assert_stringifyable_value(arg)
        ])

    def disable_features(self, *args: str):
        self.add_arguments(*[
            f"--disable-{feature}"
            for feature in args
        ])

    def build_process(self) -> ProcessBuilder:
        res = ProcessBuilder([self.path])
        res.env = self.env
        res.args.extend(self.args)
        res.args.extend([
            f"{k}={v}"
            for k, v in self.confenv.items()
        ])
        return res

    def run(self):
        cmd = self.build_process()
        cmd.run()


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


_build_impls: dict[str, type["BaseBuilder"]] = {}


class BaseBuilder(ABC):
    name: ClassVar[str] = NotImplemented

    def __init_subclass__(cls) -> None:
        this = cls.__class__
        if isabstract(cls):
            return
        if cls.name == this.name:
            raise Exception
        assert isinstance(cls.name, str)
        _build_impls[cls.name] = cls

    @abstractmethod
    def prepare(self):
        pass

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def install(self):
        pass

    @classmethod
    def get_builder(cls, name: str) -> type["BaseBuilder"]:
        builder_c = _build_impls[name]
        return builder_c
