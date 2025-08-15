from os import chdir
from pathlib import Path

from ..utils.flatten import flatten
from ..project import ComponentJob, JobPaths, Project, ProjectPaths


def walk_dedup(
    this: Project,
    component_name: str = "main",
) -> list[ComponentJob]:
    main_comp = this.components[component_name]
    main_jobs = [
        job
        for job in this.component_jobs.values()
        if job.component == main_comp
    ]
    dup_deps_2d = [
        job.walk()
        for job in main_jobs
    ]
    dup_deps = flatten(dup_deps_2d)
    all_deps = []
    for dep in dup_deps:
        if dep in all_deps:
            continue
        all_deps.append(dep)
    return all_deps


CMAKE_TOOLCHAIN_FILE = """# the name of the target operating system
set(CMAKE_SYSTEM_PROCESSOR  {arch})
set(CMAKE_SYSTEM_NAME       Linux)

set(TOOLCHAIN_PREFIX    {cross})

# which compilers to use for C and C++
set(CMAKE_C_COMPILER    ${{TOOLCHAIN_PREFIX}}-gcc)
set(CMAKE_CXX_COMPILER  ${{TOOLCHAIN_PREFIX}}-g++)

# NOTE: cmake uses -Os by default, but our version of gcc supports it
#set(CMAKE_C_FLAGS_MINSIZEREL    -Oz -DNDEBUG)
set(CMAKE_EXE_LINKER_FLAGS      -static)
"""


def prepare_for_build(this: Project):
    build_aux_dir = this.paths.build_aux_dir

    cmake_dir = build_aux_dir / "cmake"
    cmake_dir.mkdir(parents=True, exist_ok=True)
    system_targets = this.target_sets["system"]
    for target in system_targets.targets:
        arch = target.info.arch
        cross = target.get_cross()
        txt = CMAKE_TOOLCHAIN_FILE.format(
            arch=arch,
            cross=cross,
        )
        target_path = cmake_dir / f"{target.info.name2}.cmake"
        target_path.write_text(txt)


def prepare_job(
    job: ComponentJob,
    paths: ProjectPaths,
    root_dir: Path,
):
    root_dir.mkdir(parents=True, exist_ok=True)


def do_build_job_log(
    job: ComponentJob,
    paths: JobPaths,
):
    match job.component.name:
        case "lunzip":
            from ventoy_ng_cpio.builders.lunzip import build
        case "lz4":
            from ventoy_ng_cpio.builders.lz4 import build
        case "lzo":
            from ventoy_ng_cpio.builders.lzo import build
        case "xz":
            from ventoy_ng_cpio.builders.xz import build
        case "xz-embedded":
            from ventoy_ng_cpio.builders.xzminidec import build
        case "zlib":
            from ventoy_ng_cpio.builders.zlib import build
        case "zstd":
            from ventoy_ng_cpio.builders.zstd import build
        case _:
            print("Not implemented for now")
            return
    build(job, paths)


def do_build_job(
    job: ComponentJob,
    paths: ProjectPaths,
):
    job_paths = paths.with_component_job(job)
    prepare_job(job, paths, job_paths.cwd)
    chdir(job_paths.cwd)
    #with open("vtbuild.log", "wt") as file:
    #    file.write("test\n")
    do_build_job_log(job, job_paths)
    chdir(paths.cwd)


def do_build(this: Project):
    prepare_for_build(this)
    jobs = walk_dedup(this, component_name="xz-embedded")
    for i, job in enumerate(jobs):
        print(f"{i:3} - {job.name}")
        do_build_job(job, this.paths)
