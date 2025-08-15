from os import symlink
from pathlib import Path

from ..project import ComponentJob, JobPaths
from ..utils.build import MakeRunner


def do_configure(
    job: ComponentJob,
    configs_dir: Path,
    b_bin: str,
):
    target = job.target
    filename = ""
    match b_bin:
        case "ash":
            filename = "03-ash-extras.config"
            if target.info.arch == "i386":
                filename = "04-ash-lfs.config"
            elif target.info.arch == "mips64el":
                filename = "02-ash-only.config"
        case "full":
            filename = "02-custom-static.config"
        case "hexdump":
            filename = "03-hexdump.config"
            if target.info.arch == "i386":
                filename = "04-hexdump-lfs.config"
        case "xzcat":
            filename = "03-xzcat-only.config"
            if target.info.arch == "i386":
                filename = "04-xzcat-lfs.config"
        case _:
            raise ValueError
    config_file = configs_dir / filename
    symlink(config_file, ".config")


def build(job: ComponentJob, paths: JobPaths):
    comp = job.component
    target = job.target
    (b_name, b_bin) = comp.name.split("-")
    main_source = comp.sources[b_name]
    main_source_dir = paths.sources_dir / main_source.get_extracted_name()

    makefile = main_source_dir / "Makefile"

    make = MakeRunner()
    make.file = str(makefile)
    make.env["KBUILD_SRC"] = str(main_source_dir)
    make.env["CROSS_COMPILE"] = target.get_cross()
    make.env["CFLAGS"] = "-Oz"

    config_file = Path(".config")

    configs_dir = paths.project_dir
    configs_dir /= "extras"
    configs_dir /= b_name

    if not config_file.exists():
        do_configure(job, configs_dir, b_bin)

    if make.run_if_needed().is_up_to_date():
        return

    output_dir = paths.my_output_dir.absolute()

    make.envs_strict["DESTDIR"] = str(output_dir)
    make.run(["install"])
