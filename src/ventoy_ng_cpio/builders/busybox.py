from os import symlink
from pathlib import Path

from ..paths.build import BuildPaths
from ..paths.project import ProjectPaths
from ..projectv2.jobs import ComponentJob
from ..projectv2.project import Project
from ..buildutils.make import MakeCommandBuilder


def do_configure(
    job: ComponentJob,
    configs_dir: Path,
    b_bin: str,
):
    target = job.target
    use_lfs = target.get_bitness() != 64

    filename = ""

    match b_bin:
        case "ash":
            filename = "03-ash-extras.config"
            if use_lfs:
                filename = "04-ash-lfs.config"
            elif target.info.arch == "mips64el":
                filename = "02-ash-only.config"
        case "full":
            filename = "02-custom-static.config"
        case "hexdump":
            filename = "03-hexdump.config"
            if use_lfs:
                filename = "04-hexdump-lfs.config"
        case "xzcat":
            filename = "03-xzcat-only.config"
            if use_lfs:
                filename = "04-xzcat-lfs.config"
        case _:
            raise ValueError
    config_file = configs_dir / filename
    symlink(config_file, ".config")


def build(
    job: ComponentJob,
    project: Project,
    build_paths: BuildPaths,
    project_paths: ProjectPaths,
):
    comp = job.component
    target = job.target
    (b_name, b_bin) = comp.info.name.split("-")
    main_source = comp.sources[b_name]
    main_source_dir = build_paths.sources_dir / main_source.get_extracted_name()

    makefile = main_source_dir / "Makefile"

    make = MakeCommandBuilder()
    make.file = str(makefile)
    make.env["KBUILD_SRC"] = str(main_source_dir)
    make.env["CROSS_COMPILE"] = target.info.get_cross()
    make.env["CFLAGS"] = "-Oz"

    config_file = Path(".config")

    configs_dir = project_paths.project_dir
    configs_dir /= "extras"
    configs_dir /= b_name

    if not config_file.exists():
        do_configure(job, configs_dir, b_bin)

    if make.run_if_needed().is_up_to_date():
        return

    out_dir = build_paths.component_job_output_dir(job)

    make.envs_strict["DESTDIR"] = str(out_dir.absolute())
    make.run(["install"])
