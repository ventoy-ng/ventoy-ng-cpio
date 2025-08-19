from dataclasses import dataclass
from pathlib import Path

from ventoy_ng_cpio.project.components import Component
from ventoy_ng_cpio.project.jobs import ComponentJob


@dataclass(frozen=True)
class ProjectPaths:
    project_dir: Path

    @property
    def extras_dir(self) -> Path:
        return self.project_dir / "extras"

    def component_extras_dir(self, component: Component) -> Path:
        return self.extras_dir / component.info.name

    def component_job_extras_dir(self, job: ComponentJob) -> Path:
        return self.component_extras_dir(job.component)
