from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import symlink
from pathlib import Path
from shutil import copy2

from ..builders_abc.build import BaseBuilder
from ..buildutils.make import MakeCommandBuilder
from ..schemas.sources import SourceInfo


@dataclass
class BaseBusyboxBuilder(BaseBuilder, ABC):
    config_file: Path = Path(".config")

    def __post_init__(self):
        source_dir = self.get_main_source_dir()
        self.makefile = source_dir / "Makefile"
        make = MakeCommandBuilder()
        make.file = str(self.makefile)
        make.env["KBUILD_SRC"] = str(source_dir)
        make.env["CROSS_COMPILE"] = self.job.target.info.get_cross()
        make.env["CFLAGS"] = "-Oz"
        self.make = make

    def get_main_source(self) -> SourceInfo:
        return self.job.component.sources["busybox"]

    @abstractmethod
    def get_config_name(self) -> str:
        pass

    def get_config_path(self) -> Path:
        configs_dir = self.project_paths.project_dir
        configs_dir /= "extras"
        configs_dir /= "busybox"
        return configs_dir / self.get_config_name()

    def prepare(self):
        if self.config_file.exists():
            return
        target_config_file = self.get_config_path()
        symlink(target_config_file, self.config_file)

    def build(self):
        # make -q is broken here for some reason
        bin_busybox = Path("busybox")
        if bin_busybox.exists():
            return
        self.make.run()

    def install(self):
        output_dir = self.get_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)
        copy2("busybox", output_dir / "busybox")


@dataclass
class BusyboxAshBuilder(BaseBusyboxBuilder):
    NAME = "busybox-ash"

    def get_config_name(self) -> str:
        target = self.job.target
        use_lfs = target.get_bitness() != 64
        filename = "03-ash-extras.config"
        if use_lfs:
            filename = "04-ash-lfs.config"
        elif target.info.arch == "mips64el":
            filename = "02-ash-only.config"
        return filename


@dataclass
class BusyboxFullBuilder(BaseBusyboxBuilder):
    NAME = "busybox-full"

    def get_config_name(self) -> str:
        return "02-custom-static.config"
