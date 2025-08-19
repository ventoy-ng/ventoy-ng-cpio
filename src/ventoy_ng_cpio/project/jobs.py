from dataclasses import dataclass

from typing_extensions import Self

from ..utils.flatten import flatten
from .components import Component
from .targets import Target


@dataclass(frozen=True)
class ComponentJobInfo:
    pass


@dataclass
class ComponentJob:
    component: Component
    target: Target
    dependencies: dict[str, Self]

    @property
    def name(self) -> str:
        return self.component.info.name + self.target.suffix

    @classmethod
    def _new(
        cls,
        component: Component,
        target: Target,
        all_components: dict[str, Component],
        all_jobs: dict[str, Self],
    ) -> Self:
        dep_names = component.get_deps(target)
        dep_comps = [
            all_components[cname]
            for cname in dep_names
        ]
        pot_dep_jobs = [
            job
            for job in all_jobs.values()
            if job.component in dep_comps
        ]
        dep_jobs = [
            job
            for job in pot_dep_jobs
            if target.is_subtarget(job.target)
        ]
        deps = {
            job.name: job
            for job in dep_jobs
        }
        return cls(component, target, deps)  # type: ignore

    @classmethod
    def new(
        cls,
        component: Component,
        all_components: dict[str, Component],
        all_jobs: dict[str, Self],
    ) -> dict[str, Self]:
        targets = component.get_targets()
        jobs = [
            cls._new(component, target, all_components, all_jobs)
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
            new_jobs = cls.new(component, components, jobs)
            jobs.update(new_jobs)
        return jobs

    def walk(self) -> list[Self]:
        deptt = [
            dep.walk()
            for dep in self.dependencies.values()
        ]
        dept = flatten(deptt)
        return dept + [self]
