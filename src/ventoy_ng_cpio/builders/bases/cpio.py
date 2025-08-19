from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..utils.cpio import CpioCommandBuilder
from .base import BaseBuilder


@dataclass
class BaseCpioBuilder(BaseBuilder, ABC):
    @abstractmethod
    def get_cpio_name(self) -> str:
        pass

    def prepare(self):
        pass

    @abstractmethod
    def build_cpio(self):
        pass

    def build(self):
        if self.get_output_dir(absolute=False).exists():
            return
        self._flagged_for_install = True
        self.build_cpio()

    def do_install(self):
        output_dir = self.get_output_dir(absolute=False)
        output_file = output_dir / self.get_cpio_name()
        cmd = CpioCommandBuilder.get_def()
        cpio_data = cmd.run_glob(reset_mtime=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file.write_bytes(cpio_data)
        self.output_cpio_file = output_file
