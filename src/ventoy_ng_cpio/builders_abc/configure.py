from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from ..builders_abc.make import BaseMakeBuilder


@dataclass
class BaseConfigureBuilder(BaseMakeBuilder, ABC):
    def is_configured(self) -> bool:
        return self.makefile.exists()

    def get_configure_script(self) -> Path:
        main_source_dir = self.get_main_source_dir()
        return main_source_dir / "configure"

    @abstractmethod
    def do_configure(self):
        pass

    def prepare(self):
        if self.is_configured():
            return
        self.do_configure()

    def do_install(self):
        make = self.make

        make.envs_strict["DESTDIR"] = str(self.get_output_dir())
        make.run(["install"])
