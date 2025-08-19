from dataclasses import dataclass
from shutil import copy2

from ventoy_ng_cpio.project.jobs import ComponentJob

from .bases.copier import BaseCopierBuilder


@dataclass
class ArchRamdisksBuilder(BaseCopierBuilder):
    NAME = "arch-ramdisks"

    def __post_init__(self):
        self.output_dir = self.get_output_dir(absolute=False)

    def copy_output_files(self, job: ComponentJob):
        input_dir = self.get_input_dir(job)
        for input_file in input_dir.iterdir():
            output_file = self.output_dir / input_file.name
            output_file.unlink(missing_ok=True)
            copy2(input_file, output_file)

    def do_install(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for dep in self.job.dependencies.values():
            self.copy_output_files(dep)
