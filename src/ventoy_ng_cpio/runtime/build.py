from os import chdir
from pathlib import Path

from ..paths.build import BuildPaths
from ..paths.project import ProjectPaths
from ..projectv2.jobs import ComponentJob
from ..projectv2.project import Project

CMAKE_TOOLCHAIN_FILE = """# the name of the target operating system
set(CMAKE_SYSTEM_PROCESSOR  {arch})
set(CMAKE_SYSTEM_NAME       Linux)

set(TOOLCHAIN_PREFIX    {triplet})

# which compilers to use for C and C++
set(CMAKE_C_COMPILER    ${{TOOLCHAIN_PREFIX}}-gcc)
set(CMAKE_CXX_COMPILER  ${{TOOLCHAIN_PREFIX}}-g++)

# NOTE: cmake uses -Os by default, but our version of gcc supports it
#set(CMAKE_C_FLAGS_MINSIZEREL    -Oz -DNDEBUG)
set(CMAKE_EXE_LINKER_FLAGS      -static)
"""


def prepare_for_build(project: Project):
    paths = project.get_build_paths()
    build_aux_dir = paths.build_aux_dir

    cmake_dir = build_aux_dir / "cmake"
    cmake_dir.mkdir(parents=True, exist_ok=True)
    system_targets = project.target_sets["system"]
    for target in system_targets.targets:
        arch = target.info.arch
        triplet = target.info.get_triplet()
        txt = CMAKE_TOOLCHAIN_FILE.format(
            arch=arch,
            triplet=triplet.to_string(),
        )
        target_path = cmake_dir / f"{target.info.name2}.cmake"
        target_path.write_text(txt)


def prepare_job(
    job: ComponentJob,
    paths: BuildPaths,
    job_work_dir: Path,
):
    job_work_dir.mkdir(parents=True, exist_ok=True)


def do_build_job_log(
    job: ComponentJob,
    project: Project,
    build_paths: BuildPaths,
    project_paths: ProjectPaths,
):
    comp_name = job.component.info.name
    if comp_name.startswith("busybox"):
        from ventoy_ng_cpio.builders.busybox import build
        build(
            job=job,
            project=project,
            build_paths=build_paths,
            project_paths=project_paths,
        )
        return
    match comp_name:
        case "device-mapper":
            from ventoy_ng_cpio.builders.device_mapper import build
        case "lunzip":
            from ventoy_ng_cpio.builders.lunzip import build
        case "lz4":
            from ventoy_ng_cpio.builders.lz4 import build
        case "lzo":
            from ventoy_ng_cpio.builders.lzo import build
        case "xz":
            from ventoy_ng_cpio.builders.xz import build
        case "xz-embedded":
            from ventoy_ng_cpio.builders.xz_embedded import build
        case "zlib":
            from ventoy_ng_cpio.builders.zlib import build
        case "zstd":
            from ventoy_ng_cpio.builders.zstd import build
        case _:
            print("Not implemented for now")
            return
    build(
        job=job,
        project=project,
        build_paths=build_paths,
        project_paths=project_paths,
    )


def do_build_job(
    job: ComponentJob,
    project: Project,
):
    build_paths = project.get_build_paths()
    job_work = build_paths.component_job_work_dir(job)
    prepare_job(job, build_paths, job_work)

    build_paths = project.get_build_paths(relative_to=job_work)
    project_paths = project.get_project_paths(relative_to=job_work)
    chdir(job_work)
    #with open("vtbuild.log", "wt") as file:
    #    file.write("test\n")
    do_build_job_log(job, project, build_paths, project_paths)
    chdir(project.info.cwd)


def do_build(project: Project):
    prepare_for_build(project)
    jobs = project.walk_dedup()
    for i, job in enumerate(jobs):
        print(f"{i:3} - {job.name}")
        do_build_job(job, project)
