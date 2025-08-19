from dataclasses import dataclass
from pathlib import Path
from shutil import copy2

from ...project.jobs import ComponentJob
from ..bases.copier import BaseCopierBuilder

DEP_TO_BIN_NAME = {
    "device-mapper": {"dmsetup": "dmsetup"},
    "smallz4": {"smallz4cat": "lz4cat"},
    "lunzip": {"lunzip": "lunzip"},
    "squashfs": {"unsquashfs": "unsquashfs_"},
    "vblade": {"vblade": "vblade_"},
    "zstd": {"bin/zstd": "zstdcat"},
}


@dataclass
class RamdiskStage2ToolsBuilder(BaseCopierBuilder):
    NAME = "rd-stage2-tools"

    def dependency_bin_copy(
        self,
        job: ComponentJob,
        output_dir: Path,
        bin_suffix: str,
    ):
        input_dir = self.get_input_dir(job)
        bin_map = DEP_TO_BIN_NAME[job.component.info.name]
        for bin_src, bin_dest in bin_map.items():
            a = bin_suffix == "32" and bin_dest in ["lz4cat", "zstdcat"]
            if not a:
                bin_dest += bin_suffix
            copy2(input_dir / bin_src, output_dir / bin_dest)

    def do_install(self):
        target = self.job.target
        bin_suffix = target.info.suffix
        assert bin_suffix is not None
        output_dir = self.get_output_dir(absolute=False)
        output_dir.mkdir(parents=True, exist_ok=True)
        for dep in self.job.dependencies.values():
            self.dependency_bin_copy(dep, output_dir, bin_suffix)
