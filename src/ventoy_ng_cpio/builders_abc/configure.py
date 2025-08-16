from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from ..builders_abc.make import BaseMakeBuilder
from ..buildutils.make import MakeCommandBuilder


@dataclass
class BaseConfigureBuilder(BaseMakeBuilder, ABC):
    make: MakeCommandBuilder = field(default_factory=MakeCommandBuilder)

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

    def build(self):
        if self.make.run_if_needed().is_up_to_date():
            return
        self.install()

    def install(self):
        make = self.make

        make.envs_strict["DESTDIR"] = str(self.get_output_dir())
        make.run(["install"])
