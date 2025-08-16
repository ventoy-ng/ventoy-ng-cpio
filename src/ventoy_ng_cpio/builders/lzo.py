from dataclasses import dataclass
from pathlib import Path

from ..builders_abc.build import BaseBuilder
from ..buildutils.configure import ConfigureScriptBuilder
from ..buildutils.make import MakeCommandBuilder
from ..projectv2.jobs import ComponentJob


def do_configure(
    job: ComponentJob,
    configure_script: Path,
):
    conf = ConfigureScriptBuilder.new(configure_script)
    conf.add_arguments(f"--host={job.target.info.arch}-linux")
    conf.add_arguments("--prefix=/")
    conf.confenv["CC"] = job.target.get_cmd("gcc")
    conf.confenv["CFLAGS"] = "-Oz"
    conf.run()


@dataclass
class LzoBuilder(BaseBuilder):
    NAME = "lzo"

    def __post_init__(self):
        main_source_dir = self.get_main_source_dir()
        self.configure_script = main_source_dir / "configure"
        self.makefile = Path("Makefile")

    def prepare(self):
        if self.makefile.exists():
            return
        do_configure(self.job, self.configure_script)

    def build(self):
        # make -q is broken here for some reason
        lzo_libtool = Path("src/liblzo2.la")
        if lzo_libtool.exists():
            return
        make = MakeCommandBuilder()
        make.run()
        self.install()

    def install(self):
        make = MakeCommandBuilder()

        make.envs_strict["DESTDIR"] = str(self.get_output_dir())
        make.run(["install"])
