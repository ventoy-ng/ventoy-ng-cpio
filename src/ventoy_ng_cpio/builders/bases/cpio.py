from abc import ABC, abstractmethod
from dataclasses import dataclass

from ventoy_ng_cpio.builders.utils.cpio import CpioCommandBuilder

from .base import BaseBuilder


@dataclass
class BaseCpioBuilder(BaseBuilder, ABC):
    def __post_init__(self):
        self.output_dir = self.get_output_dir(absolute=False)
        self.output_cpio_file = self.output_dir / self.get_cpio_name()

    @abstractmethod
    def get_cpio_name(self) -> str:
        pass

    def should_prepare(self):
        return False

    def do_prepare(self):
        pass

    @abstractmethod
    def build_cpio(self):
        pass

    def should_build(self) -> bool:
        if super().should_build():
            return True
        return not self.output_dir.exists()

    def do_build(self):
        self.build_cpio()
        self.flags.install = True

    def do_install(self):
        cmd = CpioCommandBuilder.get_def()
        cpio_data = cmd.run_glob(reset_mtime=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_cpio_file.write_bytes(cpio_data)
