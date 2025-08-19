from dataclasses import dataclass
from pathlib import Path
from shutil import copy2

from ...project.jobs import ComponentJob
from ..bases.cpio import BaseCpioBuilder


@dataclass
class RamdiskStage1Builder(BaseCpioBuilder):
    NAME = "rd-stage1"

    def get_cpio_name(self) -> str:
        return f"ventoy_{self.job.target.info.name2}.cpio"

    def copy_stage1_dep_files(self, job: ComponentJob, output_dir: Path):
        input_dir = self.get_input_dir(job)
        for input_file in input_dir.iterdir():
            output_file = output_dir / input_file.name
            output_file.unlink(missing_ok=True)
            copy2(input_file, output_file)

    def copy_stage2_dep_files(self, job: ComponentJob, output_dir: Path):
        input_dir = self.get_input_dir(job)
        filename = "tools.cpio.xz"
        copy2(input_dir / filename, output_dir / filename)

    def build_cpio(self):
        output_dir = Path("ventoy")
        busybox_dir = output_dir / "busybox"
        busybox_dir.mkdir(parents=True, exist_ok=True)
        rd_stage1_deps = []
        rd_stage2_deps = []
        for dep in self.job.dependencies.values():
            stagename = dep.name.split("-")[1]
            if stagename == "stage2":
                rd_stage2_deps.append(dep)
                continue
            rd_stage1_deps.append(dep)
        for dep in rd_stage1_deps:
            self.copy_stage1_dep_files(dep, busybox_dir)
        for dep in rd_stage2_deps:
            self.copy_stage2_dep_files(dep, output_dir)
