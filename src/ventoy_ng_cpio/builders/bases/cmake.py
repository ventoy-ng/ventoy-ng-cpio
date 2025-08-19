from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from ventoy_ng_cpio.builders.utils.cmake import CMakeCommandBuilder
from ventoy_ng_cpio.builders.utils.make import MakeCommandBuilder
from ventoy_ng_cpio.paths.build import BuildPaths
from ventoy_ng_cpio.project.targets import Target

from .base import BaseBuilder
from .make import BaseMakeBuilder


def do_cmake_configure(
    paths: BuildPaths,
    target: Target,
    cmake_dir: Path,
    output_dir: Path,
    configure_hook: Callable[[CMakeCommandBuilder], None],
):
    cmake = CMakeCommandBuilder(source_dir=str(cmake_dir))
    cmake.install_prefix = str(output_dir)
    cmake.set_toolchain(paths, target)
    configure_hook(cmake)
    cmake.run()


@dataclass
class BaseCMakeBuilder(BaseBuilder, ABC):
    @abstractmethod
    def is_configured(self) -> bool:
        pass

    @abstractmethod
    def get_cmake_dir(self) -> Path:
        pass

    @abstractmethod
    def cmake_configure_hook(self, cmake: CMakeCommandBuilder):
        pass

    def prepare(self):
        if self.is_configured():
            return
        do_cmake_configure(
            self.build_paths,
            self.job.target,
            self.get_cmake_dir(),
            self.get_output_dir(),
            self.cmake_configure_hook,
        )


@dataclass
class CMakeDefBuilder(BaseCMakeBuilder, BaseMakeBuilder, ABC):
    make: MakeCommandBuilder = field(default_factory=MakeCommandBuilder)

    def is_configured(self) -> bool:
        return self.makefile.exists()

    def do_install(self):
        self.make.run(["install"])
