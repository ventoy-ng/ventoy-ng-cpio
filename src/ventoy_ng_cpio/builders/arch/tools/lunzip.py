from dataclasses import dataclass
from pathlib import Path

from ventoy_ng_cpio.builders.bases.configure import BaseConfigureBuilder
from ventoy_ng_cpio.builders.ext.strip_install import ExtStripInstall
from ventoy_ng_cpio.builders.utils.configure import ConfigureScriptBuilder
from ventoy_ng_cpio.project.jobs import ComponentJob


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
class LunzipBuilder(ExtStripInstall, BaseConfigureBuilder):
    NAME = "lunzip"

    def __post_init__(self):
        self.bin_name = self.job.component.info.name

    def do_prepare(self):
        do_configure(
            self.job,
            self.get_configure_script(),
        )
