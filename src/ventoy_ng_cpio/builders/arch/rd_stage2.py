from dataclasses import dataclass
from pathlib import Path
from shutil import copy2

from ...builders_abc.cpio import BaseCpioBuilder
from ...buildutils.xz import compress_file_with_xz
from ...projectv2.jobs import ComponentJob


@dataclass
class RamdiskStage2Builder(BaseCpioBuilder):
    NAME = "rd-stage2"

    def get_cpio_name(self) -> str:
        return "tools.cpio"

    def copy_dep_files(self, job: ComponentJob, output_dir: Path):
        input_dir = self.get_input_dir(job)
        for input_file in input_dir.iterdir():
            output_file = output_dir / input_file.name
            output_file.unlink(missing_ok=True)
            copy2(input_file, output_file)

    def build_cpio(self):
        output_dir = Path("tools")
        output_dir.mkdir(parents=True, exist_ok=True)
        for dep in self.job.dependencies.values():
            self.copy_dep_files(dep, output_dir)

    def do_install(self):
        super().do_install()
        compress_file_with_xz(self.output_cpio_file)
