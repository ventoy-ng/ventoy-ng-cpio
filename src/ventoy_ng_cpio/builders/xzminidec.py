from ..project import ComponentJob, JobPaths
from ..utils.build import MakeRunner


def build(job: ComponentJob, paths: JobPaths):
    comp = job.component
    main_source = comp.sources[comp.name]
    main_source_dir = paths.sources_dir / main_source.get_extracted_name()

    makefile = paths.project_dir
    makefile /= "extras"
    makefile /= comp.name
    makefile /= "Makefile"

    make = MakeRunner()
    make.file = str(makefile)
    make.env["CROSS"] = f"{job.target.get_cross()}-"
    make.envs_strict["srcdir"] = str(main_source_dir)
    if make.run_if_needed().is_up_to_date():
        return

    output_dir = paths.my_output_dir.absolute()

    make.envs_strict["DESTDIR"] = str(output_dir)
    make.run(["install"])
