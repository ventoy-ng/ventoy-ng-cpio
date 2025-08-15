from pathlib import Path

from ..project import ComponentJob, JobPaths
from ..utils.build import ConfigureScriptWrapper, MakeRunner


def do_configure(
    job: ComponentJob,
    main_source_conf: Path,
):
    conf = ConfigureScriptWrapper.new(main_source_conf)
    #conf.add_arguments(f"--host={job.target.info.arch}-linux")
    conf.add_arguments("--prefix=/")
    conf.add_arguments("--static")
    conf.env["CC"] = job.target.get_cmd("gcc")
    conf.env["CFLAGS"] = "-Oz"
    conf.run()


def build(job: ComponentJob, paths: JobPaths):
    comp = job.component
    main_source = comp.sources[comp.name]
    main_source_dir = paths.sources_dir / main_source.get_extracted_name()
    main_source_conf = main_source_dir / "configure"

    makefile = Path("Makefile")

    if not makefile.exists():
        do_configure(job, main_source_conf)
    make = MakeRunner()
    if make.run_if_needed().is_up_to_date():
        return

    output_dir = paths.my_output_dir.absolute()

    make.envs_strict["DESTDIR"] = str(output_dir)
    make.run(["install"])
