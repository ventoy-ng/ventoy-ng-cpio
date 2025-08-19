from abc import ABC
from dataclasses import dataclass, field
from os import environ
from pathlib import Path
from typing import Optional

from ventoy_ng_cpio.utils.process import ProcessBuilder


@dataclass
class BaseCommandBuilder(ABC):
    path: str
    cwd: Optional[Path] = field(default=None)
    env: dict[str, str] = field(default_factory=lambda: dict(environ))

    def _build_process_a(
        self,
    ) -> ProcessBuilder:
        res = ProcessBuilder([self.path])
        if self.cwd is not None:
            res.cwd = self.cwd
        res.env = self.env
        return res
