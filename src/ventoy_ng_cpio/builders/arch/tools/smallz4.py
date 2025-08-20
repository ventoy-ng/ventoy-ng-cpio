from dataclasses import dataclass
from pathlib import Path

from ventoy_ng_cpio.builders.ext.strip_install import ExtStripInstall
from ventoy_ng_cpio.builders.utils.cc import CcBuilder


@dataclass
class Smallz4Builder(ExtStripInstall):
    NAME = "smallz4"

    def __post_init__(self):
        self.bin_name = "smallz4cat"
        self.bin_build_path = Path(self.bin_name)

    def get_main_source_dir(self) -> Path:
        sources_dir = self.build_paths.sources_dir
        main_source = self.get_main_source()

        return sources_dir / main_source.name

    def should_prepare(self):
        return False

    def do_prepare(self):
        pass

    def should_build(self) -> bool:
        if super().should_build():
            return True
        return not self.bin_build_path.exists()

    def do_build(self):
        target = self.job.target
        cmd = CcBuilder(target.get_cmd("cc"))
        cmd.output_file = self.bin_build_path
        source_dir = self.get_main_source_dir()
        source_file = source_dir / (self.bin_name + ".c")
        cmd.args.append(str(source_file))
        cmd.args.append("-Oz")
        cmd.args.append("-MMD")
        cmd.run()
        self.flags.install = True
