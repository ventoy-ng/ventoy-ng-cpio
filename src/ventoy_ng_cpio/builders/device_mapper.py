from dataclasses import dataclass
from pathlib import Path
from shutil import copy2, copytree

from ..consts import ENCODING
from ..builders_abc.build import BaseBuilder
from ..buildutils.configure import ConfigureScriptBuilder
from ..buildutils.make import MakeCommandBuilder
from ..projectv2.jobs import ComponentJob


def do_copy_src(source_dir: Path):
    for file in source_dir.iterdir():
        if file.is_dir():
            copytree(file, file.name, copy_function=copy2)
            continue
        copy2(file, file.name)


def do_config_patch(conf_h: str) -> str:
    # fix 1: force disable rpl_malloc
    conf_h = conf_h.replace(
        "#define malloc rpl_malloc",
        "/* #undef malloc */",
    )

    return conf_h


def do_configure(job: ComponentJob):
    target = job.target
    triplet = target.info.get_triplet()
    arch = triplet.arch
    if arch == "aarch64":
        arch = "arm"

    conf = ConfigureScriptBuilder()
    conf.add_arguments("--host=" + arch + "-linux")
    conf.disable_features("nls", "selinux", "shared")
    conf.confenv["CC"] = target.get_cmd("cc")
    conf.confenv["CFLAGS"] = "-Oz"
    conf.confenv["LDFLAGS"] = "-static"
    conf.run()

    configure_header = Path("include/configure.h")
    conf_h_old = configure_header.read_text(encoding=ENCODING)
    conf_h = do_config_patch(conf_h_old)
    configure_header.write_text(conf_h, encoding=ENCODING)


@dataclass
class DeviceMapperBuilder(BaseBuilder):
    NAME = "device-mapper"

    def __post_init__(self):
        self.configure_script = Path("configure")
        self.makefile = Path("Makefile")

    def prepare(self):
        if not self.configure_script.exists():
            do_copy_src(self.get_main_source_dir())
        if self.makefile.exists():
            return
        do_configure(self.job)

    def build(self):
        # make -q is broken here for some reason
        bin_dmsetup = Path("dmsetup/dmsetup")
        if bin_dmsetup.exists():
            return
        make = MakeCommandBuilder()
        make.run()

    def install(self):
        pass
