from dataclasses import dataclass
from pathlib import Path
from shlex import join
from shutil import copy2, copytree

from ventoy_ng_cpio.builders.bases.make import BaseMakeBuilder
from ventoy_ng_cpio.builders.utils.make import MakeCommandBuilder
from ventoy_ng_cpio.builders.utils.strip import strip_bin_copy
from ventoy_ng_cpio.utils.process import ProcessBuilder


def do_copy_src(source_dir: Path):
    for file in source_dir.iterdir():
        if file.is_dir():
            copytree(file, file.name, copy_function=copy2)
            continue
        copy2(file, file.name)


ALGOS = ["gz", "xz", "lzo", "lz4", "zstd", "lzma_xz"]


@dataclass
class SquashfsBuilder(BaseMakeBuilder):
    NAME = "squashfs"
    bin_name = "unsquashfs"

    def __post_init__(self):
        make = MakeCommandBuilder()
        make.env["CC"] = self.job.target.get_cmd("cc")
        make.env["CFLAGS"] = "-Oz"
        cppflags = []
        ldflags = ["-static"]
        for alg in ALGOS:
            alg_key = alg.upper() + "_SUPPORT"
            make.env[alg_key] = "1"
        for jobd in self.job.dependencies.values():
            dep_output_dir = self.get_input_dir(jobd)
            cppflags.append("-I" + str(dep_output_dir / "include"))
            ldflags.append("-L" + str(dep_output_dir / "lib"))
        make.env["CPPFLAGS"] = join(cppflags)
        make.env["LDFLAGS"] = join(ldflags)
        self.make = make

    def get_main_source_dir(self) -> Path:
        return super().get_main_source_dir() / "squashfs-tools"

    def should_prepare(self) -> bool:
        return not self.makefile.exists()

    def do_prepare(self):
        source_dir = self.get_main_source_dir()
        do_copy_src(source_dir)
        patches_dir = self.get_extras_dir()
        for patch in patches_dir.iterdir():
            print("Applying patch", patch.name)
            cmd = ProcessBuilder(["patch"])
            cmd.args.extend(["-i", str(patch)])
            cmd.run()

    def get_make_targets(self):
        return [self.bin_name]

    def do_install(self):
        output_dir = self.get_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)
        strip_bin_copy(
            self.job.target,
            self.bin_name,
            str(output_dir / self.bin_name),
        )
