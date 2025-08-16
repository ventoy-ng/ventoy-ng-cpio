from dataclasses import dataclass, field
from pathlib import Path

from .build import BaseBuilder


def default_makefile() -> Path:
    return Path("Makefile")


@dataclass
class BaseMakeBuilder(BaseBuilder):
    makefile: Path = field(default_factory=default_makefile)
