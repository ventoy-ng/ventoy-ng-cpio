from dataclasses import dataclass

from ..builders_abc.make import BaseMakeBuilder
from ..buildutils.make import MakeCommandBuilder


@dataclass
class XzEmbeddedBuilder(BaseMakeBuilder):
    NAME = "xz-embedded"

    def __post_init__(self):
        makefile = self.project_paths.project_dir
        makefile /= "extras"
        makefile /= self.job.component.info.name
        makefile /= "Makefile"

        make = MakeCommandBuilder()
        make.file = str(makefile)
        make.env["CROSS"] = self.job.target.info.get_cross()
        make.envs_strict["srcdir"] = str(self.get_main_source_dir())
        self.make = make

    def prepare(self):
        pass

    def do_install(self):
        make = self.make

        make.envs_strict["DESTDIR"] = str(self.get_output_dir())
        make.run(["install"])
