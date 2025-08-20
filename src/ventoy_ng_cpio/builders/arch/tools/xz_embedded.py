from dataclasses import dataclass

from ventoy_ng_cpio.builders.bases.make import BaseMakeBuilder
from ventoy_ng_cpio.builders.utils.make import MakeCommandBuilder


@dataclass
class XzEmbeddedBuilder(BaseMakeBuilder):
    NAME = "xz-embedded"

    def __post_init__(self):
        self.makefile = self.get_extras_dir() / "Makefile"

        make = MakeCommandBuilder()
        make.file = str(self.makefile)
        make.env["CROSS"] = self.job.target.info.get_cross()
        make.envs_strict["srcdir"] = str(self.get_main_source_dir())
        self.make = make

    def should_prepare(self) -> bool:
        return False

    def do_prepare(self):
        pass
