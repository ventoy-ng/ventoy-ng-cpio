from dataclasses import dataclass
from pathlib import Path
from shlex import join

from ventoy_ng_cpio.builders.bases.make import BaseMakeBuilder
from ventoy_ng_cpio.builders.utils.make import MakeCommandBuilder
from ventoy_ng_cpio.project.targets import Target


def get_target_flag(target: Target) -> str:
    match target.info.arch:
        case "x86_64":
            return "-DVTOY_X86_64"
        case "i386":
            return "-DVTOY_I386"
        case "aarch64":
            return "-DVTOY_AA64"
        case "mips64el":
            return "-DVTOY_MIPS64"
        case _:
            raise ValueError


@dataclass
class VToyToolBuilder(BaseMakeBuilder):
    NAME = "vtoytool"

    def __post_init__(self):
        self.makefile = self.get_extras_dir() / "Makefile"

        cppflags = [
            # Needed even for musl
            "-DUSE_DIET_C",
            # Needed for newer versions
            "-Duint8_t=u_int8_t",
            get_target_flag(self.job.target),
        ]

        make = MakeCommandBuilder()
        make.file = str(self.makefile)
        make.env["CROSS"] = self.job.target.info.get_cross()
        make.env["CFLAGS"] = "-Oz"
        make.env["CPPFLAGS"] = join(cppflags)
        make.envs_strict["srcdir"] = str(self.get_main_source_dir())
        self.make = make

    def get_main_source_dir(self) -> Path:
        return super().get_main_source_dir() / "src"

    def should_prepare(self) -> bool:
        return False

    def do_prepare(self):
        pass
