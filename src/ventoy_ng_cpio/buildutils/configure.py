from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

from ..utils.process import ProcessBuilder
from ..utils.string import assert_stringifyable_value
from ..utils.path import PathLike
from .base_run import BaseCommandRunner


def default_configure_name() -> Path:
    return Path("./configure")


@dataclass
class ConfigureScriptWrapper(BaseCommandRunner):
    path: str = field(default="./configure")
    args: list[str] = field(default_factory=list)
    confenv: dict[str, str] = field(default_factory=dict)

    @classmethod
    def new(cls, path: PathLike) -> Self:
        return cls(str(path))

    def add_arguments(self, *args: object):
        self.args.extend([
            str(arg)
            for arg in args
            if assert_stringifyable_value(arg)
        ])

    def disable_features(self, *args: str):
        self.add_arguments(*[
            f"--disable-{feature}"
            for feature in args
        ])

    def build_process(self) -> ProcessBuilder:
        res = ProcessBuilder([self.path])
        res.env = self.env
        res.args.extend(self.args)
        res.args.extend([
            f"{k}={v}"
            for k, v in self.confenv.items()
        ])
        return res

    def run(self):
        cmd = self.build_process()
        cmd.run()
