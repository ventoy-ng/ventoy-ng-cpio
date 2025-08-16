from dataclasses import dataclass
from pathlib import Path
from shlex import join
from shutil import copy2, copytree

from ..builders_abc.make import BaseMakeBuilder
from ..buildutils.make import MakeCommandBuilder
from ..buildutils.strip import strip_bin_copy


def do_copy_src(source_dir: Path):
    for file in source_dir.iterdir():
        if file.is_dir():
            copytree(file, file.name, copy_function=copy2)
            continue
        copy2(file, file.name)


@dataclass
class VBladeBuilder(BaseMakeBuilder):
    NAME = "vblade"
    bin_name = "vblade"

    def __post_init__(self):
        self.makefile = Path("makefile")
        make = MakeCommandBuilder()
        # NOTE: doesn't accept LDFLAGS
        # also -fcommon is needed to avoid multiple definitions
        cc = join([self.job.target.get_cmd("cc"), "-static", "-fcommon"])
        make.envs_strict["CC"] = cc
        make.envs_strict["CFLAGS"] = "-Oz -Wall"
        self.make = make

    def prepare(self):
        if self.makefile.exists():
            return
        do_copy_src(self.get_main_source_dir())

    def install(self):
        output_dir = self.get_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)
        strip_bin_copy(
            self.job.target,
            self.bin_name,
            str(output_dir / self.bin_name),
        )
