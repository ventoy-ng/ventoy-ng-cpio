from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ...utils.process import ProcessBuilder
from .base import BaseCommandBuilder


@dataclass
class CcBuilder(BaseCommandBuilder):
    path: str = field(default="cc")
    output_file: Optional[Path] = None
    args: list[str] = field(default_factory=list)

    def build_process(
        self,
    ) -> ProcessBuilder:
        res = super()._build_process_a()
        if self.output_file is not None:
            res.args.extend(["-o", str(self.output_file)])
        res.args.extend(self.args)
        return res

    def run(self):
        cmd = self.build_process()
        print(*cmd.args)
        cmd.run()
