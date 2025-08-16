from pathlib import Path
from shutil import copy2, copytree

from ..buildutils.configure import ConfigureScriptBuilder
from ..buildutils.make import MakeCommandBuilder
from ..buildutils.strip import strip_bin_copy
from ..paths.build import BuildPaths
from ..paths.project import ProjectPaths
from ..projectv2.jobs import ComponentJob
from ..projectv2.project import Project


def do_copy_src(
    source_dir: Path,
):
    for file in source_dir.iterdir():
        if file.is_dir():
            copytree(file, file.name, copy_function=copy2)
            continue
        copy2(file, file.name)


def do_config_patch(
    conf_h: str,
) -> str:
    # fix 1: force disable rpl_malloc
    conf_h = conf_h.replace(
        "#define malloc rpl_malloc",
        "/* #undef malloc */",
    )

    return conf_h


def do_configure(
    job: ComponentJob,
    configure_script: Path,
):
    target = job.target
    triplet = target.info.get_triplet()
    arch = triplet.arch
    if arch == "aarch64":
        arch = "arm"

    cexec = "./" + str(configure_script)
    conf = ConfigureScriptBuilder.new(cexec)
    conf.add_arguments("--host=" + arch + "-linux")
    conf.disable_features("nls", "selinux", "shared")
    conf.confenv["CC"] = target.get_cmd("cc")
    conf.confenv["CFLAGS"] = "-Oz"
    conf.confenv["LDFLAGS"] = "-static"
    conf.run()

    configure_header = Path("include/configure.h")
    conf_h_old = configure_header.read_text()
    conf_h = do_config_patch(conf_h_old)
    configure_header.write_text(conf_h)


def build(
    job: ComponentJob,
    project: Project,
    build_paths: BuildPaths,
    project_paths: ProjectPaths,
):
    comp = job.component
    main_source = comp.sources[comp.info.name]
    main_source_dir = build_paths.sources_dir / main_source.get_extracted_name()

    configure = Path("configure")

    if not configure.exists():
        do_copy_src(main_source_dir)

    makefile = Path("Makefile")

    if not makefile.exists():
        do_configure(job, configure)
    make = MakeCommandBuilder()
    if make.run_if_needed().is_up_to_date():
        return

    out_dir = build_paths.component_job_output_dir(job)

    #make.envs_strict["DESTDIR"] = str(out_dir.absolute())
    #make.run(["install"])
