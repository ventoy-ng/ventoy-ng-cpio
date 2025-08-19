from os import symlink

from ventoy_ng_cpio.project.project import Project
from ventoy_ng_cpio.schemas.sources import SourceInfo


def prepare_submodule_source(this: SourceInfo, project: Project):
    print("Linking", repr(this.name))
    build_paths = project.get_build_paths()
    build_sources_dir = build_paths.sources_dir
    destination_dir = build_sources_dir / this.get_extracted_name()
    project_sources_dir = project.get_sources_paths(
        relative_to=build_sources_dir,
    )
    dest_dir = project_sources_dir.sources_dir / this.name
    destination_dir.unlink(missing_ok=True)
    symlink(dest_dir, destination_dir)
