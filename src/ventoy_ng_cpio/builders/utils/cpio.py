from dataclasses import dataclass, field
from glob import glob
from os import utime
from typing import Optional

from typing_extensions import Self

from ...utils.process import ProcessBuilder
from .base import BaseCommandBuilder


def reset_mtime_for_files(files: list[str]):
    for filename in files:
        utime(filename, (0, 0))


@dataclass
class CpioCommandBuilder(BaseCommandBuilder):
    path: str = field(default="cpio")
    output_format: Optional[str] = field(default=None)
    owner: Optional[str] = field(default=None)
    renumber_inodes: bool = field(default=False)
    use_null: bool = field(default=False)

    @classmethod
    def get_def(cls) -> Self:
        return cls(
            output_format="newc",
            owner="root:root",
            renumber_inodes=True,
        )

    def build_process(self) -> ProcessBuilder:
        res = super()._build_process_a()
        res.args.append("-o")
        if self.output_format is not None:
            res.args.append("--format=" + self.output_format)
        if self.owner is not None:
            res.args.append("--owner=" + self.owner)
        if self.renumber_inodes:
            res.args.append("--renumber-inodes")
        res.pipe_stdin()
        return res

    def run(self, files: list[str]) -> bytes:
        files_as_txt = "\n".join(files)
        file_stream = files_as_txt.encode()
        cmd = self.build_process()
        cmd.pipe_stdout()
        p = cmd.spawn()
        (stdout, _) = p.communicate(input=file_stream)
        assert isinstance(stdout, bytes)
        p.success()
        return stdout

    def run_glob(
        self,
        pathname: str = "**",
        recursive: bool = True,
        do_sort: bool = True,
        reset_mtime: bool = False,
    ) -> bytes:
        files = glob(pathname, root_dir=self.cwd, recursive=recursive)
        if do_sort:
            files.sort()
        if reset_mtime:
            reset_mtime_for_files(files)
        return self.run(files)
