from dataclasses import dataclass
from pathlib import Path

from ventoy_ng_cpio.builders.bases.configure import BaseConfigureBuilder
from ventoy_ng_cpio.builders.utils.configure import ConfigureScriptBuilder
from ventoy_ng_cpio.project.jobs import ComponentJob


def do_configure(
    job: ComponentJob,
    configure_script: Path,
):
    target = job.target
    conf = ConfigureScriptBuilder.new(configure_script)
    conf.add_arguments(f"--host={job.target.info.arch}-linux")
    conf.add_arguments("--prefix=/")
    conf.add_arguments(
        "--enable-lib",
        "--enable-static=yes",
        "--enable-shared=no",
        "--enable-util=no",
        "--enable-example=no",
    )
    conf.confenv["CC"] = target.get_cmd("cc")
    conf.confenv["CFLAGS"] = "-Oz"
    conf.run()


@dataclass
class LibFuse2Builder(BaseConfigureBuilder):
    NAME = "libfuse2"

    def do_prepare(self):
        do_configure(
            self.job,
            self.get_configure_script(),
        )
