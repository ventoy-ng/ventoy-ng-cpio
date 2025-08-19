from copy import copy
from dataclasses import dataclass, field
from os import environ
from pathlib import Path
from subprocess import PIPE, Popen
from typing import IO, TYPE_CHECKING, Any, Optional, TypeAlias

if TYPE_CHECKING:
    from _typeshed import FileDescriptor


FileLike: TypeAlias = IO[Any] | "FileDescriptor" | None


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
    stdin: FileLike = field(default=None)
    stdout: FileLike = field(default=None)
    stderr: FileLike = field(default=None)

    def copy(self):
        return ProcessBuilder(
            args=copy(self.args),
            cwd=copy(self.cwd),
            env=copy(self.env),
        )

    def pipe_stdin(self):
        self.stdin = PIPE

    def pipe_stdout(self):
        self.stdout = PIPE

    def pipe_stderr(self):
        self.stdout = PIPE

    def spawn(self):
        return PopenX(
            self.args,
            stdin=self.stdin,
            stdout=self.stdout,
            stderr=self.stderr,
            cwd=self.cwd,
            env=self.env,
        )

    def run(self):
        self.spawn().success()
