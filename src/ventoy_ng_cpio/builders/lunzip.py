from dataclasses import dataclass
from pathlib import Path

from ..builders_abc.build import BaseBuilder
from ..buildutils.configure import ConfigureScriptBuilder
from ..buildutils.make import MakeCommandBuilder
from ..buildutils.strip import strip_bin_copy
from ..projectv2.jobs import ComponentJob


def do_configure(
    job: ComponentJob,
    configure_script: Path,
):
    target = job.target
    conf = ConfigureScriptBuilder.new(configure_script)
    conf.confenv["CC"] = target.get_cmd("cc")
    conf.confenv["CFLAGS"] = "-Oz"
    conf.confenv["CPPFLAGS"] = "-Wall -W"
    conf.confenv["LDFLAGS"] = "-static"
    conf.run()


@dataclass
class LunzipBuilder(BaseBuilder):
    NAME = "lunzip"

    def prepare(self):
        main_source_dir = self.get_main_source_dir()
        main_source_conf = main_source_dir / "configure"

        makefile = Path("Makefile")

        if not makefile.exists():
            do_configure(self.job, main_source_conf)

    def build(self):
        make = MakeCommandBuilder()
        if make.run_if_needed().is_up_to_date():
            return
        self.install()

    def install(self):
        out_dir = self.get_output_dir()
        out_dir.mkdir(parents=True, exist_ok=True)
        strip_bin_copy(
            self.job.target,
            self.job.component.info.name,
            str(out_dir / self.job.component.info.name),
        )
