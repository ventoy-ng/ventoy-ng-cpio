from ventoy_ng_cpio.project.project import Project
from ventoy_ng_cpio.schemas.sources import SourceInfo

from .link import prepare_submodule_source
from .remote import prepare_remote_source


def do_prepare_source(source: SourceInfo, project: Project):
    if source.url is not None:
        prepare_remote_source(source, project)
        return
    if source.submod:
        prepare_submodule_source(source, project)
        return
    raise NotImplementedError(source.name)


def do_prepare(project: Project):
    for source in project.sources.values():
        do_prepare_source(source, project)
