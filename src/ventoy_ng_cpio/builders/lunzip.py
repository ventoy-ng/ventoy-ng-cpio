from dataclasses import dataclass
from pathlib import Path

from ..builders_abc.configure import BaseConfigureBuilder
from ..buildutils.configure import ConfigureScriptBuilder
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
class LunzipBuilder(BaseConfigureBuilder):
    NAME = "lunzip"

    def do_configure(self):
        do_configure(
            self.job,
            self.get_configure_script(),
        )

    def do_install(self):
        out_dir = self.get_output_dir()
        out_dir.mkdir(parents=True, exist_ok=True)
        strip_bin_copy(
            self.job.target,
            self.job.component.info.name,
            str(out_dir / self.job.component.info.name),
        )
