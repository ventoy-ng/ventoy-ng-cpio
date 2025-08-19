from abc import ABC
from dataclasses import dataclass

from .base import BaseBuilder


@dataclass
class BaseCopierBuilder(BaseBuilder, ABC):
    def prepare(self):
        pass

    def build(self):
        if self.get_output_dir(absolute=False).exists():
            return
        self._flagged_for_install = True
