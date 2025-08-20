from dataclasses import dataclass
from pathlib import Path
from shutil import copy2, copytree, rmtree

from ventoy_ng_cpio.builders.bases.cpio import BaseCpioBuilder
from ventoy_ng_cpio.builders.utils.xz import compress_file_with_xz
from ventoy_ng_cpio.project.jobs import ComponentJob


def autocopy(src: Path, dst: Path):
    if src.is_dir():
        copytree(src, dst, dirs_exist_ok=True)
    else:
        copy2(src, dst)


@dataclass
class RamdiskStage2Builder(BaseCpioBuilder):
    NAME = "rd-stage2"

    def get_cpio_name(self) -> str:
        return "tools.cpio"

    def copy_dep_files(self, job: ComponentJob, output_dir: Path):
        input_dir = self.get_input_dir(job)
        for input_file in input_dir.iterdir():
            output_file = output_dir / input_file.name
            autocopy(input_file, output_file)

    def build_cpio(self):
        output_dir = Path("tools")
        if output_dir.exists():
            rmtree(output_dir)
        output_dir.mkdir(parents=True)
        for dep in self.job.dependencies.values():
            self.copy_dep_files(dep, output_dir)

    def do_install(self):
        super().do_install()
        compress_file_with_xz(self.output_cpio_file)
