from dataclasses import dataclass
from pathlib import Path

from ventoy_ng_cpio.builders.bases.simplesource import SimpleSourceBuilder
from ventoy_ng_cpio.utils.path import PathLike


@dataclass
class VtChmodBuilder(SimpleSourceBuilder):
    NAME = "vtchmod"

    def __post_init__(self):
        self.bin_name = self.job.component.info.name
        self.bin_build_path = Path(self.bin_name)

    def get_main_source_dir(self) -> Path:
        return super().get_main_source_dir() / "src"

    def get_source_files(self) -> list[PathLike]:
        return [self.bin_name + ".c"]
