from dataclasses import dataclass
from pathlib import Path

from ventoy_ng_cpio.builders.bases.cmake import CMakeDefBuilder
from ventoy_ng_cpio.builders.utils.cmake import CMakeCommandBuilder


@dataclass
class Lz4Builder(CMakeDefBuilder):
    NAME = "lz4"

    def get_cmake_dir(self) -> Path:
        return self.get_main_source_dir() / "build/cmake"

    def cmake_configure_hook(self, cmake: CMakeCommandBuilder):
        pass

    def make_should_build(self) -> bool:
        # make -q is broken here due to symlinks
        lib_lz4 = Path("liblz4.a")
        return not lib_lz4.exists()
