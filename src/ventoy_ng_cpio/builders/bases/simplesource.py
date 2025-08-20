from abc import abstractmethod
from pathlib import Path

from ventoy_ng_cpio.builders.ext.strip_install import ExtStripInstall
from ventoy_ng_cpio.builders.utils.cc import CcBuilder
from ventoy_ng_cpio.utils.path import PathLike


class SimpleSourceBuilder(ExtStripInstall):
    bin_build_path: Path

    def should_prepare(self):
        return False

    def do_prepare(self):
        pass

    def should_build(self) -> bool:
        if super().should_build():
            return True
        return not self.bin_build_path.exists()

    @abstractmethod
    def get_source_files(self) -> list[PathLike]:
        pass

    def compiler_args_hook(self, cc: CcBuilder):
        pass

    def do_build(self):
        target = self.job.target
        cmd = CcBuilder(target.get_cmd("cc"))
        cmd.output_file = self.bin_build_path
        source_dir = self.get_main_source_dir()
        cmd.args.extend(
            [str(source_dir / src) for src in self.get_source_files()]
        )
        cmd.args.append("-static")
        cmd.args.append("-Oz")
        cmd.args.append("-MMD")
        self.compiler_args_hook(cmd)
        cmd.run()
        self.flags.install = True
