from dataclasses import dataclass
from pathlib import Path
from shutil import copy2, copytree

from ..builders_abc.configure import BaseConfigureBuilder
from ..buildutils.configure import ConfigureScriptBuilder
from ..buildutils.strip import strip_bin_copy
from ..consts import ENCODING
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
class DeviceMapperBuilder(BaseConfigureBuilder):
    NAME = "device-mapper"
    bin_name = "dmsetup"
    bin_path = Path("dmsetup/dmsetup")

    def get_configure_script(self) -> Path:
        return Path("configure")

    def do_configure(self):
        do_configure(self.job)

    def prepare(self):
        configure_script = Path("configure")
        if not configure_script.exists():
            do_copy_src(self.get_main_source_dir())
        super().prepare()

    def build(self):
        # make -q is broken here for some reason
        if self.bin_path.exists():
            return
        self.make.run()
        self.install()

    def install(self):
        output_dir = self.get_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)
        strip_bin_copy(
            self.job.target,
            str(self.bin_path),
            str(output_dir / self.bin_name),
        )
