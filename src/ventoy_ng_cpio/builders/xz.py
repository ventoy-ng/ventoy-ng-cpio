from pathlib import Path

from ..paths.build import BuildPaths
from ..paths.project import ProjectPaths
from ..projectv2.jobs import ComponentJob
from ..projectv2.project import Project
from ..utils.build import ConfigureScriptWrapper, MakeRunner


def do_configure(
    job: ComponentJob,
    main_source_conf: Path,
):
    conf = ConfigureScriptWrapper.new(main_source_conf)
    conf.add_arguments(f"--host={job.target.info.arch}-linux")
    conf.add_arguments("--prefix=/")
    conf.add_arguments("--enable-shared=no", "--enable-static=yes")
    conf.disable_features(
        "xz", "xzdec",
        "lzmadec", "lzmainfo", "lzma-links",
        "scripts", "assembler",
    )
    conf.confenv["CC"] = job.target.get_cmd("gcc")
    conf.confenv["CFLAGS"] = "-Oz"
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
    make = MakeRunner()
    if make.run_if_needed().is_up_to_date():
        return

    out_dir = build_paths.component_job_output_dir(job)

    make.envs_strict["DESTDIR"] = str(out_dir.absolute())
    make.run(["install"])
