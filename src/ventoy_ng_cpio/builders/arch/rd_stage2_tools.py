from dataclasses import dataclass
from pathlib import Path
from shutil import copy2

from ventoy_ng_cpio.builders.bases.copier import BaseCopierBuilder
from ventoy_ng_cpio.project.jobs import ComponentJob


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
    elif info.name == "vtoy_fuse_iso":
        binname = "vtoy_fuse_iso"
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

    def copy_vtoytool(self, job: ComponentJob, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        suffix = job.target.info.suffix
        assert suffix is not None
        input_dir = self.get_input_dir(job)
        bin_name = job.component.info.name
        output_file = bin_name + "_" + suffix
        copy2(input_dir / bin_name, output_dir / output_file)

    def do_install(self):
        output_dir = self.get_output_dir(absolute=False)
        output_dir.mkdir(parents=True, exist_ok=True)
        deps = list(self.job.dependencies.values())
        vtoytool_job = next(
            dep for dep in deps if dep.component.info.name == "vtoytool"
        )
        deps.remove(vtoytool_job)
        for dep in deps:
            self.copy_output_bins(dep, output_dir)
        self.copy_vtoytool(vtoytool_job, output_dir / "vtoytool/00")
