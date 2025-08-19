from dataclasses import dataclass
from pathlib import Path

from ...bases.cmake import CMakeDefBuilder
from ...utils.cmake import CMakeCommandBuilder


@dataclass
class Lz4Builder(CMakeDefBuilder):
    NAME = "lz4"

    def get_cmake_dir(self) -> Path:
        return self.get_main_source_dir() / "build/cmake"

    def cmake_configure_hook(self, cmake: CMakeCommandBuilder):
        pass

    def build(self):
        # make -q is broken here due to symlinks
        lib_lz4 = Path("liblz4.a")
        if lib_lz4.exists():
            return
        self._flagged_for_install = True
        self.make.run()
