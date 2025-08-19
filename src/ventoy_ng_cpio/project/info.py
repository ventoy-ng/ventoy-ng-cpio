from dataclasses import dataclass
from itertools import chain
from os import getcwd
from pathlib import Path

from typing_extensions import Self

from ..schemas.components import ComponentInfo
from ..schemas.sources import SourceInfo
from ..schemas.targets import TargetInfo


def load_target_info(project_dir: Path) -> dict[Path, TargetInfo]:
    targets_dir = project_dir / "targets"
    target_files = [
        filename
        for filename in chain(
            targets_dir.glob("system/*"),
            targets_dir.glob("output/*"),
        )
        if filename.is_file()
    ]
    return {
        target_file: TargetInfo.from_toml(target_file.read_text())
        for target_file in target_files
    }


def load_source_info(project_dir: Path) -> dict[Path, SourceInfo]:
    sources_dir = project_dir / "sources"
    return {
        source_file: SourceInfo.from_toml(source_file.read_text())
        for source_file in sources_dir.iterdir()
    }


def load_component_info(project_dir: Path) -> dict[Path, ComponentInfo]:
    comp_index_path = project_dir / "components.lst"
    comp_index = comp_index_path.read_text()
    comp_dir = project_dir / "components"

    res: dict[Path, ComponentInfo] = {}

    for line in comp_index.splitlines():
        if not line or line.startswith("#"):
            continue
        comp_path = comp_dir / line
        comp_txt = comp_path.read_text()
        comp_info = ComponentInfo.from_toml(comp_txt)
        res[comp_path] = comp_info

    return res


@dataclass(frozen=True)
class ProjectInfoX:
    cwd: Path
    root: Path
    targets: dict[Path, TargetInfo]
    sources: dict[Path, SourceInfo]
    components: dict[Path, ComponentInfo]

    @classmethod
    def load(cls, project_dir: Path) -> Self:
        cwd = Path(getcwd())
        targets = load_target_info(project_dir)
        sources = load_source_info(project_dir)
        components = load_component_info(project_dir)
        return cls(
            cwd, project_dir,
            targets, sources, components,
        )

    def get_root_abspath(self) -> Path:
        return self.cwd / self.root
