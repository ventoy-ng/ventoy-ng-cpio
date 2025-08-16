from dataclasses import dataclass, field
from re import Pattern
from typing import Optional

from mashumaro.mixins.toml import DataClassTOMLMixin


@dataclass(frozen=True)
class ComponentPerTargetInfo(DataClassTOMLMixin):
    rule: Pattern
    sources: list[str] = field(default_factory=list)
    deps: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ComponentInfo(DataClassTOMLMixin):
    name: str
    target_set: Optional[str] = field(default=None)
    sources: list[str] = field(default_factory=list)
    deps: list[str] = field(default_factory=list)
    per_target: list[ComponentPerTargetInfo] = field(default_factory=list)
