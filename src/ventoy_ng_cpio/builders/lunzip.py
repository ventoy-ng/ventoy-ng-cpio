from pathlib import Path

from ..buildutils.configure import ConfigureScriptBuilder
from ..buildutils.make import MakeCommandBuilder
from ..buildutils.strip import strip_bin_copy
from ..paths.build import BuildPaths
from ..paths.project import ProjectPaths
from ..projectv2.jobs import ComponentJob
from ..projectv2.project import Project


def do_configure(
    job: ComponentJob,
    main_source_conf: Path,
):
    target = job.target
    conf = ConfigureScriptBuilder.new(main_source_conf)
    conf.confenv["CC"] = target.get_cmd("gcc")
    conf.confenv["CFLAGS"] = "-Oz"
    conf.confenv["CPPFLAGS"] = "-Wall -W"
    conf.confenv["LDFLAGS"] = "-static"
    conf.run()


def build(
    job: ComponentJob,
    project: Project,
    build_paths: BuildPaths,
    project_paths: ProjectPaths,
):
    comp = job.component
    main_source = comp.sources[comp.info.name]
    main_source_dir = build_paths.sources_dir / main_source.get_extracted_name()
    main_source_conf = main_source_dir / "configure"

    makefile = Path("Makefile")

    if not makefile.exists():
        do_configure(job, main_source_conf)
    make = MakeCommandBuilder()
    if make.run_if_needed().is_up_to_date():
        return
    out_dir = build_paths.component_job_output_dir(job)
    out_dir.mkdir(parents=True, exist_ok=True)
    strip_bin_copy(
        job.target,
        job.component.info.name,
        str(out_dir / job.component.info.name),
    )
