from dataclasses import dataclass
from pathlib import Path
from shutil import copy2

from ...project.jobs import ComponentJob
from ..bases.copier import BaseCopierBuilder


def rd_stage_2_bin_rename(job: ComponentJob) -> tuple[str, str]:
    info = job.component.info
    target = job.target
    suffix = target.info.suffix
    assert suffix is not None

    isuffix = "" if target.info.arch == "i386" else suffix

    if info.name == "smallz4":
        return ("smallz4cat", "lz4cat" + isuffix)
    if info.name == "zstd":
        return ("bin/zstd", "zstdcat" + isuffix)

    extra_suffix = ""

    if info.name == "device-mapper":
        binname = "dmsetup"
    elif info.name == "lunzip":
        binname = "lunzip"
    elif info.name == "squashfs":
        binname = "unsquashfs"
        extra_suffix = "_"
    elif info.name == "vblade":
        binname = "vblade"
        extra_suffix = "_"
    else:
        raise NotImplementedError(job.name)

    return (binname, binname + extra_suffix + suffix)


@dataclass
class RamdiskStage2ToolsBuilder(BaseCopierBuilder):
    NAME = "rd-stage2-tools"

    def copy_output_bins(self, job: ComponentJob, output_dir: Path):
        input_dir = self.get_input_dir(job)
        (bin_src, bin_dest) = rd_stage_2_bin_rename(job)
        copy2(input_dir / bin_src, output_dir / bin_dest)

    def do_install(self):
        output_dir = self.get_output_dir(absolute=False)
        output_dir.mkdir(parents=True, exist_ok=True)
        for dep in self.job.dependencies.values():
            self.copy_output_bins(dep, output_dir)
