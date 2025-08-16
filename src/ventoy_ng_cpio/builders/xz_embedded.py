from dataclasses import dataclass

from ..builders_abc.build import BaseBuilder
from ..buildutils.make import MakeCommandBuilder


@dataclass
class XzEmbeddedBuilder(BaseBuilder):
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
        self.make_instance = make

    def prepare(self):
        pass

    def build(self):
        make = self.make_instance
        if make.run_if_needed().is_up_to_date():
            return
        self.install()

    def install(self):
        make = self.make_instance

        make.envs_strict["DESTDIR"] = str(self.get_output_dir())
        make.run(["install"])
