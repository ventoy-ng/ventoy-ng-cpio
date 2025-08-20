from dataclasses import dataclass
from pathlib import Path

from ventoy_ng_cpio.builders.bases.configure import BaseConfigureBuilder
from ventoy_ng_cpio.builders.utils.configure import ConfigureScriptBuilder
from ventoy_ng_cpio.project.jobs import ComponentJob


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
class ZlibBuilder(BaseConfigureBuilder):
    NAME = "zlib"

    def do_prepare(self):
        do_configure(
            self.job,
            self.get_configure_script(),
        )
