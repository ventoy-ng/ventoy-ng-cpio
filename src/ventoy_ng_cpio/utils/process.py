from copy import copy
from dataclasses import dataclass, field
from os import environ
from pathlib import Path
from subprocess import Popen
from typing import Optional


class PopenX(Popen):
    def success(self):
        ret = self.wait()
        if ret == 0:
            return
        raise RuntimeError(ret)


@dataclass
class ProcessBuilder:
    args: list[str] = field(default_factory=list)
    cwd: Optional[Path] = None
    env: dict[str, str] = field(default_factory=lambda: dict(environ))

    def copy(self):
        return ProcessBuilder(
            args=copy(self.args),
            cwd=copy(self.cwd),
            env=copy(self.env),
        )

    def spawn(self):
        return PopenX(self.args, cwd=self.cwd, env=self.env)

    def run(self):
        self.spawn().success()
