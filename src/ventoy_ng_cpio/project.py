from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, Optional, Self

from .paths import BUILD_DIR
from .schema import (
    ComponentInfo, ProjectInfo, SourceInfo, TargetInfo,
)
from .utils.path import PathLike, pathlike_to_path


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    build_dir: Path = field(default=BUILD_DIR)

    @property
    def project_toml_file(self) -> Path:
        return self.root / "project.toml"

    @property
    def archives_dir(self) -> Path:
        return self.build_dir / "archives"

    @property
    def sources_dir(self) -> Path:
        return self.build_dir / "sources"

    @property
    def work_dir(self) -> Path:
        return self.build_dir / "work"


@dataclass(frozen=True)
class Target:
    info: TargetInfo
    subtargets: Optional[list[Self]]
    _match_any_subtarget: bool = False
    _default_instance: ClassVar[Optional[Self]] = None

    @classmethod
    def new(
        cls,
        info: TargetInfo,
        targets: Optional[dict[str, Self]] = None,
    ) -> Self:
        if info.subtargets is not None:
            if targets is None:
                raise ValueError
            subtargets = [
                targets[subtarget_name]
                for subtarget_name in info.subtargets
            ]
        else:
            subtargets = None
        return cls(info, subtargets)  # type: ignore

    @classmethod
    def new_for(cls, tgtinfo: list[TargetInfo]) -> dict[str, Self]:
        targets: dict[str, Self] = {}
        for info in tgtinfo:
            target = cls.new(info, targets)
            targets[info.name] = target
        return targets

    @classmethod
    def default(cls) -> Self:
        if cls._default_instance is not None:
            return cls._default_instance
        info = TargetInfo(
            name="TARGETLESS",
            triplet=None,
            suffix=None,
            use_suffix=False,
            subtargets=None,
        )
        cls._default_instance = cls(
            info,
            None,
            _match_any_subtarget=True,
        )
        return cls._default_instance

    def is_default(self) -> bool:
        return self is self.default()

    @property
    def suffix(self) -> str:
        if self.is_default():
            return ""
        suf = self.info.name.split("/")[1]
        return f"-{suf}"

    def is_subtarget(self, other: Self) -> bool:
        if other is self:
            return True
        if not self.subtargets:
            return False
        return any([
            target.is_subtarget(other)
            for target in self.subtargets
        ])


@dataclass(frozen=True)
class TargetSet:
    name: str
    targets: list[Target]

    @classmethod
    def new_for(
        cls,
        targets: dict[str, Target],
    ) -> dict[str, Self]:
        target_sets: dict[str, list[Target]] = {}
        for tname, target in targets.items():
            tset = tname.split("/")[0]
            if tset not in target_sets:
                target_sets[tset] = []
            tseta = target_sets[tset]
            tseta.append(target)
        return {
            name: cls(name, info)
            for name, info in target_sets.items()
        }


@dataclass
class Component:
    info: ComponentInfo
    target_set: Optional[TargetSet]
    sources: dict[str, SourceInfo]
    dependencies: dict[str, Self]

    @classmethod
    def new(
        cls,
        info: ComponentInfo,
        all_target_sets: dict[str, TargetSet],
        all_sources: dict[str, SourceInfo],
        all_components: dict[str, Self],
    ) -> Self:
        if info.target_set:
            target_set = all_target_sets[info.target_set]
        else:
            target_set = None
        sources = {
            src_name: all_sources[src_name]
            for src_name in info.sources
        }
        dependencies = {
            comp_name: all_components[comp_name]
            for comp_name in info.deps
        }
        return cls(info, target_set, sources, dependencies)  # type: ignore

    @classmethod
    def new_for(
        cls,
        comp_info: list[ComponentInfo],
        all_target_sets: dict[str, TargetSet],
        all_sources: dict[str, SourceInfo],
    ) -> dict[str, Self]:
        components: dict[str, Self] = {}
        for info in comp_info:
            comp = cls.new(
                info,
                all_target_sets,
                all_sources,
                components,
            )
            components[info.name] = comp
        return components

    @property
    def name(self) -> str:
        return self.info.name


@dataclass
class ComponentPaths:
    paths: ProjectPaths
    component: Component

    @property
    def main_dir(self) -> Path:
        return self.paths.build_dir / self.component.name

    @property
    def sources_dir(self) -> Path:
        return self.main_dir / "sources"

    def work_dir(self, component_job: "ComponentJob") -> Path:
        dirname = "work" + component_job.target.suffix
        return self.main_dir / dirname


@dataclass
class ComponentJob:
    component: Component
    target: Target
    dependencies: dict[str, Self]

    @property
    def name(self) -> str:
        return self.component.name + self.target.suffix

    @classmethod
    def _new(
        cls,
        component: Component,
        target: Target,
        all_jobs: dict[str, Self],
    ) -> Self:
        deps: dict[str, Self] = {}
        for comp in component.dependencies.values():
            matching_jobs_list = [
                job
                for job in all_jobs.items()
                if all([
                    job[1].component is comp,
                    target.is_subtarget(job[1].target),
                ])
            ]
            matching_jobs = dict(matching_jobs_list)
            deps.update(matching_jobs)
        return cls(component, target, deps)  # type: ignore

    @classmethod
    def new(
        cls,
        component: Component,
        all_jobs: dict[str, Self],
    ) -> dict[str, Self]:
        target_set = component.target_set
        if target_set is None:
            targets = [Target.default()]
        else:
            targets = target_set.targets
        jobs = [
            cls._new(component, target, all_jobs)
            for target in targets
        ]
        return {
            job.name: job
            for job in jobs
        }

    @classmethod
    def new_for(
        cls,
        components: dict[str, Component],
    ) -> dict[str, Self]:
        jobs: dict[str, Self] = {}
        for component in components.values():
            new_jobs = cls.new(component, jobs)
            jobs.update(new_jobs)
        return jobs


@dataclass(repr=False)
class Project:
    paths: ProjectPaths
    info: ProjectInfo
    targets: dict[str, Target]
    target_sets: dict[str, TargetSet]
    sources: dict[str, SourceInfo]
    components: dict[str, Component]
    component_jobs: dict[str, ComponentJob]

    @classmethod
    def new(cls, paths: ProjectPaths, info: ProjectInfo) -> Self:
        targets = Target.new_for(info.target)
        target_sets = TargetSet.new_for(targets)
        sources = {
            src.name: src
            for src in info.sources
        }
        components = Component.new_for(info.components, target_sets, sources)
        component_jobs = ComponentJob.new_for(components)
        this = cls(
            paths, info, targets, target_sets, sources,
            components, component_jobs,
        )
        return this

    @classmethod
    def load(cls, project_dir: PathLike) -> Self:
        project_dirx = pathlike_to_path(project_dir)
        paths = ProjectPaths(project_dirx)
        with paths.project_toml_file.open("rt") as file:
            info = ProjectInfo.from_toml(file.read())
        return cls.new(paths, info)
