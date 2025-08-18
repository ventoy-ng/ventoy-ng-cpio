from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Self

from ventoy_ng_cpio.utils.path import PathLike

from ..buildutils.base_run import BaseCommandBuilder
from ..utils.process import ProcessBuilder


@dataclass
class XzCommandBuilder(BaseCommandBuilder):
    path: str = field(default="xz")
    compression_preset: Optional[int] = field(default=None)
    extreme: bool = field(default=False)

    @classmethod
    def get_def(cls) -> Self:
        return cls(
            compression_preset=9,
            extreme=True,
        )

    def build_process(self) -> ProcessBuilder:
        res = super()._build_process_a()
        if self.compression_preset is not None:
            preset = self.compression_preset
            res.args.append("-" + str(preset))
        if self.extreme:
            res.args.append("-e")
        res.args.append("--")
        return res

    def run(self, *args: PathLike):
        cmd = self.build_process()
        cmd.args.extend([
            str(arg)
            for arg in args
        ])
        cmd.run()


def compress_file_with_xz(filename: Path):
    #cmd = ProcessBuilder(["xz"])
    #cmd.args.append(preset)
    #cmd.args.append("--")
    #cmd.args.append(str(filename))
    #cmd.run()
    cmd = XzCommandBuilder.get_def()
    cmd.run(filename)
