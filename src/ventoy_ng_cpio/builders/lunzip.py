from pathlib import Path

from ..project import ComponentJob, JobPaths
from ..utils.build import ConfigureScriptWrapper, MakeRunner, strip_bin_copy


def do_configure(
    job: ComponentJob,
    main_source_conf: Path,
):
    target = job.target
    conf = ConfigureScriptWrapper.new(main_source_conf)
    conf.confenv["CC"] = target.get_cmd("gcc")
    conf.confenv["CFLAGS"] = "-Oz"
    conf.confenv["CPPFLAGS"] = "-Wall -W"
    conf.confenv["LDFLAGS"] = "-static"
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
    paths.my_output_dir.mkdir(parents=True, exist_ok=True)
    strip_bin_copy(
        job.target,
        job.component.name,
        str(paths.my_output_dir / job.component.name),
    )
