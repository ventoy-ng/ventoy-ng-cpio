from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ventoy_ng_cpio.builders.utils.make import MakeCommandBuilder

from .base import BaseBuilder


def default_makefile() -> Path:
    return Path("Makefile")


@dataclass
class BaseMakeBuilder(BaseBuilder):
    makefile: Path = field(default_factory=default_makefile)
    make: MakeCommandBuilder = field(default_factory=MakeCommandBuilder)

    def get_make_targets(self) -> Optional[list[str]]:
        return None

    def make_should_build(self) -> bool:
        return self.make.question(self.get_make_targets())

    def should_build(self) -> bool:
        if super().should_build():
            return True
        return self.make_should_build()

    def do_build(self):
        self.make.run(self.get_make_targets())
        self.flags.install = True

    def do_install(self):
        make = self.make

        make.envs_strict["DESTDIR"] = str(self.get_output_dir())
        make.run(["install"])
