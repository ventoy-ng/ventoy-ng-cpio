from dataclasses import dataclass
from pathlib import Path
from shlex import join
from shutil import copy2, copytree

from ventoy_ng_cpio.builders.bases.make import BaseMakeBuilder
from ventoy_ng_cpio.builders.ext.strip_install import ExtStripInstall
from ventoy_ng_cpio.builders.utils.make import MakeCommandBuilder


def do_copy_src(source_dir: Path):
    for file in source_dir.iterdir():
        if file.is_dir():
            copytree(file, file.name, copy_function=copy2)
            continue
        copy2(file, file.name)


@dataclass
class VBladeBuilder(ExtStripInstall, BaseMakeBuilder):
    NAME = "vblade"

    def __post_init__(self):
        self.bin_name = self.job.component.info.name
        self.makefile = Path("makefile")
        make = MakeCommandBuilder()
        # NOTE: doesn't accept LDFLAGS
        # also -fcommon is needed to avoid multiple definitions
        cc = join([self.job.target.get_cmd("cc"), "-static", "-fcommon"])
        make.envs_strict["CC"] = cc
        make.envs_strict["CFLAGS"] = "-Oz -Wall"
        self.make = make

    def should_prepare(self):
        return not self.makefile.exists()

    def do_prepare(self):
        do_copy_src(self.get_main_source_dir())
