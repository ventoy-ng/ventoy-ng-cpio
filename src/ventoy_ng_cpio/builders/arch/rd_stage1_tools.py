from dataclasses import dataclass
from pathlib import Path
from shutil import copy2

from ...project.jobs import ComponentJob
from ..bases.copier import BaseCopierBuilder
from ..utils.xz import compress_file_with_xz


def rd_stage_2_cvt(job: ComponentJob) -> list[tuple[str, str]]:
    info = job.component.info
    target = job.target
    if info.name == "busybox-ash":
        if target.info.arch == "x86_64":
            return [("busybox", "64h")]
        if target.info.arch == "aarch64":
            return [("busybox", "a64")]
        if target.info.arch == "mips64el":
            return [("busybox", "m64")]
        return [("busybox", "ash")]
    binsuffix = target.info.suffix
    assert binsuffix is not None
    if info.name == "busybox-full":
        binname = "busybox"
    elif info.name == "xz-embedded":
        binname = "xzminidec"
    else:
        raise NotImplementedError(job.name)
    return [(binname, binname + binsuffix)]


@dataclass
class RamdiskStage1ToolsBuilder(BaseCopierBuilder):
    NAME = "rd-stage1-tools"

    def copy_output_bins(self, job: ComponentJob, output_dir: Path):
        input_dir = self.get_input_dir(job)
        for bin_src, bin_dest in rd_stage_2_cvt(job):
            output_file = output_dir / bin_dest
            copy2(input_dir / bin_src, output_file)
            if not bin_dest.startswith("busybox"):
                continue
            compress_file_with_xz(output_file)

    def do_install(self):
        output_dir = self.get_output_dir(absolute=False)
        output_dir.mkdir(parents=True, exist_ok=True)
        for dep in self.job.dependencies.values():
            self.copy_output_bins(dep, output_dir)
