from dataclasses import dataclass
from pathlib import Path

from ..builders_abc.configure import BaseConfigureBuilder
from ..buildutils.configure import ConfigureScriptBuilder
from ..projectv2.jobs import ComponentJob


def do_configure(
    job: ComponentJob,
    configure_script: Path,
):
    conf = ConfigureScriptBuilder.new(configure_script)
    conf.add_arguments(f"--host={job.target.info.arch}-linux")
    conf.add_arguments("--prefix=/")
    conf.add_arguments("--enable-shared=no", "--enable-static=yes")
    conf.disable_features(
        "xz", "xzdec",
        "lzmadec", "lzmainfo", "lzma-links",
        "scripts", "assembler",
    )
    conf.confenv["CC"] = job.target.get_cmd("cc")
    conf.confenv["CFLAGS"] = "-Oz"
    conf.run()


@dataclass
class XzBuilder(BaseConfigureBuilder):
    NAME = "xz"

    def do_configure(self):
        do_configure(
            self.job,
            self.get_configure_script(),
        )

    def build(self):
        # make -q is broken here for some reason
        lib_lzma = Path("src/liblzma/.libs/liblzma.a")
        if lib_lzma.exists():
            return
        self.make.run()
        self.install()
