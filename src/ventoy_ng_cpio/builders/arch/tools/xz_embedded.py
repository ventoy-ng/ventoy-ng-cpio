from dataclasses import dataclass

from ...bases.make import BaseMakeBuilder
from ...utils.make import MakeCommandBuilder


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

    def prepare(self):
        pass

    def do_install(self):
        make = self.make

        make.envs_strict["DESTDIR"] = str(self.get_output_dir())
        make.run(["install"])
