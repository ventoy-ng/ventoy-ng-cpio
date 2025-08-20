from abc import ABC
from dataclasses import dataclass
from pathlib import Path

from .make import BaseMakeBuilder


@dataclass
class BaseConfigureBuilder(BaseMakeBuilder, ABC):
    def is_configured(self) -> bool:
        return self.makefile.exists()

    def get_configure_script(self) -> Path:
        main_source_dir = self.get_main_source_dir()
        return main_source_dir / "configure"

    def should_prepare(self) -> bool:
        return not self.is_configured()
