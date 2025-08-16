from dataclasses import dataclass
from pathlib import Path

from ventoy_ng_cpio.buildutils.cc import CcBuilder

from ..buildutils.strip import strip_bin_copy
from ..utils.process import ProcessBuilder
from ..builders_abc.build import BaseBuilder


@dataclass
class Smallz4Builder(BaseBuilder):
    NAME = "smallz4"

    def __post_init__(self):
        self.bin_name = "smallz4cat"
        self.bin_build_path = Path(self.bin_name)

    def get_main_source_dir(self) -> Path:
        sources_dir = self.build_paths.sources_dir
        main_source = self.get_main_source()

        return sources_dir / main_source.name

    def prepare(self):
        pass

    def build(self):
        if self.bin_build_path.exists():
            return
        target = self.job.target
        cmd = CcBuilder(target.get_cmd("cc"))
        cmd.output_file = self.bin_build_path
        source_dir = self.get_main_source_dir()
        source_file = source_dir / (self.bin_name + ".c")
        cmd.args.append(str(source_file))
        cmd.args.append("-Oz")
        cmd.args.append("-MMD")
        cmd.run()
        self.install()

    def install(self):
        output_dir = self.get_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)
        strip_bin_copy(
            self.job.target,
            str(self.bin_name),
            str(output_dir / self.bin_name),
        )
