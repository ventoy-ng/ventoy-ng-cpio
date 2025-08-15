from pathlib import Path

from ..project import ComponentJob, JobPaths
from ..utils.build import CMakeBuilder, MakeRunner, NinjaRunner


def do_configure(
    job: ComponentJob,
    paths: JobPaths,
    main_source_cmake: Path,
):
    target = job.target
    cmake = CMakeBuilder(source_dir=str(main_source_cmake))
    cmake.install_prefix = str(paths.my_output_dir.absolute())
    cmake.set_toolchain(paths, target)
    cmake.generator = "Ninja"
    #cmake.args["ZSTD_BUILD_SHARED"] = "OFF"
    #cmake.args["ZSTD_PROGRAMS_LINK_SHARED"] = "OFF"
    cmake.run()


def build(job: ComponentJob, paths: JobPaths):
    comp = job.component
    sources_dir = paths.sources_dir
    main_source = comp.sources[comp.name]
    main_source_dir = sources_dir / main_source.get_extracted_name()
    main_source_cmake = main_source_dir / "build/cmake"

    #makefile = Path("Makefile")
    makefile = Path("build.ninja")

    if not makefile.exists():
        do_configure(job, paths, main_source_cmake)
    #make = MakeWrapper()
    #if make.run_if_needed().is_up_to_date():
    #    return

    ninja = NinjaRunner()
    if ninja.run_if_needed().is_up_to_date():
        return

    #output_dir = paths.my_output_dir.absolute()

    #make.envs_strict["DESTDIR"] = str(output_dir)
    #make.run(["install"])

    #ninja.env["DESTDIR"] = str(output_dir)
    ninja.run(["install"])
