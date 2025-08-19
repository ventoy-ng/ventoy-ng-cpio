import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from typing_extensions import Self

from ventoy_ng_cpio.schemas.components import ComponentInfo
from ventoy_ng_cpio.schemas.sources import SourceInfo

from .targets import Target, TargetSet


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
            src_name: all_sources[src_name] for src_name in info.sources
        }
        dependencies = {
            comp_name: all_components[comp_name] for comp_name in info.deps
        }
        this = cls(info, target_set, sources, dependencies)  # type: ignore
        return this

    @classmethod
    def new_for(
        cls,
        comp_info: dict[Path, ComponentInfo],
        all_target_sets: dict[str, TargetSet],
        all_sources: dict[str, SourceInfo],
    ) -> dict[str, Self]:
        components: dict[str, Self] = {}
        for info in comp_info.values():
            comp = cls.new(
                info,
                all_target_sets,
                all_sources,
                components,
            )
            components[info.name] = comp
        return components

    def get_targets(self) -> list[Target]:
        if self.target_set is None:
            return [Target.default()]
        return self.target_set.targets

    def get_deps(self, target: Optional[Target] = None) -> list[str]:
        deps = self.info.deps.copy()
        if target is None or target.is_default():
            return deps
        for pt_info in self.info.per_target:
            m = re.match(pt_info.rule, target.info.name2)
            if m is None:
                continue
            for dep in pt_info.deps:
                if dep.startswith("!"):
                    deps.remove(dep[1:])
                else:
                    deps.append(dep)
        return deps
