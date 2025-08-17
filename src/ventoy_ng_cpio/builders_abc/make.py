from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..buildutils.make import MakeCommandBuilder
from .build import BaseBuilder


def default_makefile() -> Path:
    return Path("Makefile")


@dataclass
class BaseMakeBuilder(BaseBuilder):
    makefile: Path = field(default_factory=default_makefile)
    make: MakeCommandBuilder = field(default_factory=MakeCommandBuilder)

    def get_make_targets(self) -> Optional[list[str]]:
        return None

    def build(self):
        targets = self.get_make_targets()
        if self.make.run_if_needed(targets).is_up_to_date():
            return
        self._flagged_for_install = True
