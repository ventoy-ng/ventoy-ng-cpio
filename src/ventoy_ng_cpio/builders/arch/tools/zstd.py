from dataclasses import dataclass
from pathlib import Path

from ...bases.cmake import CMakeDefBuilder
from ...utils.cmake import CMakeCommandBuilder


@dataclass
class ZstdBuilder(CMakeDefBuilder):
    NAME = "zstd"

    def get_cmake_dir(self) -> Path:
        return self.get_main_source_dir() / "build/cmake"

    def cmake_configure_hook(self, cmake: CMakeCommandBuilder):
        cmake.args["ZSTD_BUILD_SHARED"] = "OFF"
        cmake.args["ZSTD_PROGRAMS_LINK_SHARED"] = "OFF"

    def build(self):
        # make -q is broken here due to symlinks
        zstd_bin = Path("programs/zstd")
        if zstd_bin.exists():
            return
        self._flagged_for_install = True
        self.make.run()
