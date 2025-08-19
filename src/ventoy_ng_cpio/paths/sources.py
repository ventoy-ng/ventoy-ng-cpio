from dataclasses import dataclass
from pathlib import Path

# from ventoy_ng_cpio.project.components import Component
# from ventoy_ng_cpio.project.jobs import ComponentJob


@dataclass(frozen=True)
class SourcesPaths:
    sources_dir: Path
