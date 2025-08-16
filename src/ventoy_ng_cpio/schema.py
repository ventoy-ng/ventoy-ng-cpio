from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional
from urllib.parse import ParseResult, urlparse

from mashumaro import field_options
from mashumaro.mixins.toml import DataClassTOMLMixin

from .schemas.targets import TargetInfo
from .schemas.sources import SourceInfo



@dataclass(frozen=False)
class ProjectInfo(DataClassTOMLMixin):
    name: str
