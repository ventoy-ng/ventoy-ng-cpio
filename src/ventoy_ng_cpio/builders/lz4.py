from dataclasses import dataclass
from pathlib import Path

from ..builders_abc.build import BaseBuilder
from ..buildutils.cmake import CMakeCommandBuilder
from ..buildutils.make import MakeCommandBuilder
from ..paths.build import BuildPaths
from ..projectv2.jobs import ComponentJob


def do_configure(
    job: ComponentJob,
    paths: BuildPaths,
    main_source_cmake: Path,
    out_dir: Path,
):
    target = job.target

    cmake = CMakeCommandBuilder(source_dir=str(main_source_cmake))
    cmake.install_prefix = str(out_dir.absolute())
    cmake.set_toolchain(paths, target)
    cmake.run()


@dataclass
class Lz4Builder(BaseBuilder):
    NAME = "lz4"

    def __post_init__(self):
        main_source_dir = self.get_main_source_dir()
        self.cmake_dir = main_source_dir / "build/cmake"
        self.makefile = Path("Makefile")

    def prepare(self):
        if self.makefile.exists():
            return
        do_configure(
            self.job,
            self.build_paths,
            self.cmake_dir,
            self.get_output_dir(),
        )

    def build(self):
        # make -q is broken here due to symlinks
        lib_lz4 = Path("liblz4.a")
        if lib_lz4.exists():
            return
        make = MakeCommandBuilder()
        make.run()
        self.install()

    def install(self):
        make = MakeCommandBuilder()
        make.run(["install"])
