from pathlib import Path

from ventoy_ng_cpio.builders.bases.base import BaseBuilder
from ventoy_ng_cpio.builders.utils.strip import strip_bin_copy


class ExtStripInstall(BaseBuilder):
    bin_name: str

    def get_bin_work_path(self) -> Path:
        return Path(self.bin_name)

    def get_bin_output_path(self) -> Path:
        output_dir = self.get_output_dir(absolute=False)
        return output_dir / self.bin_name

    def should_install(self):
        if super().should_install():
            return True
        return not self.get_bin_output_path().exists()

    def do_install(self):
        output_dir = self.get_output_dir(absolute=False)
        output_dir.mkdir(parents=True, exist_ok=True)
        bin_src = self.get_bin_work_path()
        bin_dest = self.get_bin_output_path()
        strip_bin_copy(self.job.target, str(bin_src), str(bin_dest))
