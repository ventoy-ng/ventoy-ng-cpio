import re
from dataclasses import dataclass
from os.path import relpath
from pathlib import Path
from typing import Optional

from typing_extensions import Self

from ..paths.build import BuildPaths
from ..paths.project import ProjectPaths
from ..schemas.sources import SourceInfo
from ..utils.flatten import flatten
from ..utils.path import PathLike
from .components import Component
from .info import ProjectInfoX
from .jobs import ComponentJob
from .targets import Target, TargetSet


@dataclass(repr=False)
class Project:
    build_dir: Path
    info: ProjectInfoX
    targets: dict[str, Target]
    target_sets: dict[str, TargetSet]
    sources: dict[str, SourceInfo]
    components: dict[str, Component]
    component_jobs: dict[str, ComponentJob]

    @classmethod
    def new(cls, info: ProjectInfoX, build_dir: Path) -> Self:
        targets = Target.new_for(info.targets)
        target_sets = TargetSet.new_for(targets)
        sources = {src.name: src for src in info.sources.values()}

        components = Component.new_for(
            info.components,
            target_sets,
            sources,
        )

        component_jobs = ComponentJob.new_for(components)

        this = cls(
            build_dir,
            info,
            targets,
            target_sets,
            sources,
            components,
            component_jobs,
        )
        return this

    @classmethod
    def load(cls, root: PathLike, build_dir: PathLike) -> Self:
        project_dir = Path(root)
        build_dir = Path(build_dir)
        info = ProjectInfoX.load(project_dir)
        return cls.new(info, build_dir)

    def get_build_paths(
        self,
        relative_to: Optional[PathLike] = None,
    ) -> BuildPaths:
        if relative_to is not None:
            p = Path(relpath(self.build_dir, relative_to))
        else:
            p = self.build_dir
        return BuildPaths(p)

    def get_project_paths(
        self,
        relative_to: Optional[PathLike] = None,
    ) -> ProjectPaths:
        if relative_to is not None:
            p = Path(relpath(self.info.root, relative_to))
        else:
            p = self.info.root
        return ProjectPaths(p)

    def walk_dedup(
        self,
        component_names: Optional[list[str]] = None,
        target_filter: Optional[str] = None,
    ) -> list[ComponentJob]:
        if component_names is None:
            component_names = ["main"]
        # 1 - find the requested components
        main_comp = [
            self.components[comp_name] for comp_name in component_names
        ]
        # 2 - find the jobs of those components
        main_jobs = [
            job
            for job in self.component_jobs.values()
            if job.component in main_comp
        ]
        # 2.1 - only select jobs that match user-given regex
        if target_filter is not None:
            pat = re.compile(target_filter)

            def matches_user_pattern(job: ComponentJob) -> bool:
                return pat.match(job.target.info.name) is not None

            main_jobs = list(filter(matches_user_pattern, main_jobs))
        # 3 - walk the dependency tree for each of those jobs
        dup_deps_2d = [job.walk() for job in main_jobs]
        # 4 - flatten to get one list
        dup_deps = flatten(dup_deps_2d)
        # 5 - de-duplicate
        all_deps = []
        for dep in dup_deps:
            if dep in all_deps:
                continue
            all_deps.append(dep)
        return all_deps
