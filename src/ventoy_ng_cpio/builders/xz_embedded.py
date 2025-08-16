from ..paths.build import BuildPaths
from ..paths.project import ProjectPaths
from ..projectv2.jobs import ComponentJob
from ..projectv2.project import Project
from ..buildutils.make import MakeRunner


def build(
    job: ComponentJob,
    project: Project,
    build_paths: BuildPaths,
    project_paths: ProjectPaths,
):
    comp = job.component
    main_source = comp.sources[comp.info.name]
    main_source_dir = build_paths.sources_dir / main_source.get_extracted_name()

    makefile = project_paths.project_dir
    makefile /= "extras"
    makefile /= comp.info.name
    makefile /= "Makefile"

    make = MakeRunner()
    make.file = str(makefile)
    make.env["CROSS"] = job.target.info.get_cross()
    make.envs_strict["srcdir"] = str(main_source_dir)
    if make.run_if_needed().is_up_to_date():
        return

    out_dir = build_paths.component_job_output_dir(job)

    make.envs_strict["DESTDIR"] = str(out_dir.absolute())
    make.run(["install"])
