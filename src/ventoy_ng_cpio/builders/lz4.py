from pathlib import Path

from ..paths.build import BuildPaths
from ..paths.project import ProjectPaths
from ..projectv2.jobs import ComponentJob
from ..projectv2.project import Project
from ..buildutils.cmake import CMakeBuilder
from ..buildutils.make import MakeRunner, NinjaRunner


def do_configure(
    job: ComponentJob,
    paths: BuildPaths,
    main_source_cmake: Path,
):
    target = job.target
    out_dir = paths.component_job_output_dir(job)

    cmake = CMakeBuilder(source_dir=str(main_source_cmake))
    cmake.install_prefix = str(out_dir.absolute())
    cmake.set_toolchain(paths, target)
    cmake.generator = "Ninja"
    #cmake.args["ZSTD_BUILD_SHARED"] = "OFF"
    #cmake.args["ZSTD_PROGRAMS_LINK_SHARED"] = "OFF"
    cmake.run()


def build(
    job: ComponentJob,
    project: Project,
    build_paths: BuildPaths,
    project_paths: ProjectPaths,
):
    comp = job.component
    sources_dir = build_paths.sources_dir
    main_source = comp.sources[comp.info.name]
    main_source_dir = sources_dir / main_source.get_extracted_name()
    main_source_cmake = main_source_dir / "build/cmake"

    #makefile = Path("Makefile")
    makefile = Path("build.ninja")

    if not makefile.exists():
        do_configure(job, build_paths, main_source_cmake)
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
