from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional
from urllib.parse import ParseResult, urlparse

from mashumaro import field_options
from mashumaro.mixins.toml import DataClassTOMLMixin

from .schemas.targets import TargetInfo
from .schemas.sources import SourceInfo

@dataclass(frozen=True)
class ComponentInfo(DataClassTOMLMixin):
    name: str
    target_set: Optional[str] = field(default=None)
    sources: list[str] = field(default_factory=list)
    deps: list[str] = field(default_factory=list)
    build_file: Optional[Path] = field(default=None)
    build_args: Optional[Any] = field(default=None)


@dataclass(frozen=False)
class ProjectInfo(DataClassTOMLMixin):
    name: str
    components: list[ComponentInfo]
    target: list[TargetInfo] = field(default_factory=list)
    sources: list[SourceInfo] = field(default_factory=list)
