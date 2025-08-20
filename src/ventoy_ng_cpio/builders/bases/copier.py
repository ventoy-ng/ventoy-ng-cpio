from abc import ABC
from dataclasses import dataclass

from .base import BaseBuilder


@dataclass
class BaseCopierBuilder(BaseBuilder, ABC):
    def should_prepare(self) -> bool:
        return False

    def do_prepare(self):
        pass

    def do_build(self):
        pass

    def should_install(self) -> bool:
        return not self.get_output_dir(absolute=False).exists()
