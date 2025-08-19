from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from inspect import isabstract
from pathlib import Path
from typing import ClassVar

from ...paths.build import BuildPaths
from ...paths.project import ProjectPaths
from ...project.jobs import ComponentJob
from ...project.project import Project
from ...schemas.sources import SourceInfo

_build_impls: dict[str, type["BaseBuilder"]] = {}


@dataclass
class BaseBuilder(ABC):
    job: ComponentJob
    project: Project
    build_paths: BuildPaths
    project_paths: ProjectPaths
    _flagged_for_install: bool = field(default=False)
    NAME: ClassVar[str] = ""

    def __init_subclass__(cls) -> None:
        if isabstract(cls):
            return
        if not cls.NAME:
            raise NotImplementedError(cls.__name__)
        assert isinstance(cls.NAME, str)
        _build_impls[cls.NAME] = cls

    def get_main_source(self) -> SourceInfo:
        comp = self.job.component
        return comp.sources[comp.info.name]

    def get_main_source_dir(self) -> Path:
        sources_dir = self.build_paths.sources_dir
        main_source = self.get_main_source()

        return sources_dir / main_source.get_extracted_name()

    def get_input_dir(self, job: ComponentJob):
        return self.build_paths.component_job_output_dir(job)

    def get_output_dir(self, absolute: bool = True) -> Path:
        out_dir = self.build_paths.component_job_output_dir(self.job)
        if absolute:
            out_dir = out_dir.absolute()
        return out_dir

    @abstractmethod
    def prepare(self):
        pass

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def do_install(self):
        pass

    def install(self):
        if not self._flagged_for_install:
            return
        self.do_install()


def get_builder(name: str) -> type[BaseBuilder]:
    builder_c = _build_impls[name]
    return builder_c
