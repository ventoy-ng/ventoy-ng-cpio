from dataclasses import dataclass
from pathlib import Path

from ..builders_abc.make import BaseMakeBuilder
from ..buildutils.configure import ConfigureScriptBuilder
from ..buildutils.make import MakeCommandBuilder
from ..projectv2.jobs import ComponentJob


def do_configure(
    job: ComponentJob,
    configure_script: Path,
):
    conf = ConfigureScriptBuilder.new(configure_script)
    conf.add_arguments("--prefix=/")
    conf.add_arguments("--static")
    conf.env["CC"] = job.target.get_cmd("cc")
    conf.env["CFLAGS"] = "-Oz"
    conf.run()


@dataclass
class ZlibBuilder(BaseMakeBuilder):
    NAME = "zlib"

    def __post_init__(self):
        main_source_dir = self.get_main_source_dir()
        self.configure_script = main_source_dir / "configure"
        self.make = MakeCommandBuilder()

    def prepare(self):
        if self.makefile.exists():
            return
        do_configure(self.job, self.configure_script)

    def build(self):
        if self.make.run_if_needed().is_up_to_date():
            return
        self.install()

    def install(self):
        make = self.make

        make.envs_strict["DESTDIR"] = str(self.get_output_dir())
        make.run(["install"])
