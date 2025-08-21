from dataclasses import dataclass
from pathlib import Path

from ventoy_ng_cpio.builders.bases.simplesource import SimpleSourceBuilder
from ventoy_ng_cpio.builders.utils.cc import CcBuilder
from ventoy_ng_cpio.utils.path import PathLike


@dataclass
class VToyFuseIsoBuilder(SimpleSourceBuilder):
    NAME = "vtoy_fuse_iso"

    def __post_init__(self):
        self.bin_name = self.job.component.info.name
        self.bin_build_path = Path(self.bin_name)

    def get_main_source_dir(self) -> Path:
        return super().get_main_source_dir() / "src"

    def get_source_files(self) -> list[PathLike]:
        return [self.bin_name + ".c"]

    def compiler_args_hook(self, cc: CcBuilder):
        fuse_job = next(iter(self.job.dependencies.values()))
        fuse_dir = self.get_input_dir(fuse_job)
        extra_args = [
            "-D_FILE_OFFSET_BITS=64",
            "-lfuse",
            "-I" + str(fuse_dir / "include"),
            "-L" + str(fuse_dir / "lib"),
        ]
        cc.args.extend(extra_args)
