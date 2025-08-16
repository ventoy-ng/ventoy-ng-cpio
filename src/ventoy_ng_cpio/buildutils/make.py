from abc import ABC
from dataclasses import dataclass, field
from enum import Enum, auto
from os import cpu_count
from typing import Optional

from ..utils.process import ProcessBuilder
from .base_run import BaseCommandBuilder


@dataclass
class MakeLikeCommandBuilder(BaseCommandBuilder, ABC):
    file: Optional[str] = field(default=None)

    def _build_process_b(
        self,
    ) -> ProcessBuilder:
        res = super()._build_process_a()
        if self.file is not None:
            res.args.extend(["-f", self.file])
        return res


class MakeStatus(Enum):
    Done = 0
    UpToDate = auto()
    #Failed = auto()

    def is_up_to_date(self) -> bool:
        return self == self.__class__.UpToDate


@dataclass
class MakeCommandBuilder(MakeLikeCommandBuilder):
    path: str = field(default="make")
    jobs: Optional[int] = field(default_factory=cpu_count)
    envs_strict: dict[str, str] = field(default_factory=dict)

    def build_process(
        self,
        targets: Optional[list[str]] = None,
    ) -> ProcessBuilder:
        res = super()._build_process_b()
        if self.jobs is not None:
            res.args.extend(["-O", "-j", str(self.jobs)])
        if self.envs_strict:
            res.args.extend([
                f"{k}={v}"
                for k, v in self.envs_strict.items()
            ])
        if targets:
            res.args.append("--")
            res.args.extend(targets)
        return res

    def run(
        self,
        targets: Optional[list[str]] = None,
    ):
        cmd = self.build_process(targets)
        cmd.run()

    def run_if_needed(
        self,
        targets: Optional[list[str]] = None,
    ):
        cmd = self.build_process(targets)
        cmd_check = cmd.copy()
        cmd_check.args.insert(1, "-q")
        if cmd_check.spawn().wait() == 0:
            return MakeStatus.UpToDate
        cmd.run()
        return MakeStatus.Done


@dataclass
class NinjaCommandRunner(MakeLikeCommandBuilder):
    path: str = field(default="ninja")

    def build_process(
        self,
        targets: Optional[list[str]] = None,
    ) -> ProcessBuilder:
        res = super()._build_process_b()
        res.args.append("--verbose")
        if targets:
            res.args.append("--")
            res.args.extend(targets)
        return res

    def run(
        self,
        targets: Optional[list[str]] = None,
    ):
        cmd = self.build_process(targets)
        cmd.run()

    def run_if_needed(
        self,
        targets: Optional[list[str]] = None,
    ):
        cmd = self.build_process(targets)
        cmd_check = cmd.copy()
        cmd_check.args.insert(1, "--quiet")
        if cmd_check.spawn().wait() == 0:
            return MakeStatus.UpToDate
        cmd.run()
        return MakeStatus.Done
