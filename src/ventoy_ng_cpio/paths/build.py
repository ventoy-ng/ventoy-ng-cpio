from dataclasses import dataclass
from pathlib import Path

from ..project.components import Component
from ..project.jobs import ComponentJob


@dataclass(frozen=True)
class BuildPaths:
    build_dir: Path

    @property
    def archives_dir(self) -> Path:
        return self.build_dir / "archives"

    @property
    def build_aux_dir(self) -> Path:
        return self.build_dir / "build-aux"

    @property
    def output_dir(self) -> Path:
        return self.build_dir / "output"

    @property
    def sources_dir(self) -> Path:
        return self.build_dir / "sources"

    @property
    def work_dir(self) -> Path:
        return self.build_dir / "work"

    def component_work_dir(self, component: Component) -> Path:
        return self.build_dir / "work" / component.info.name

    def component_job_work_dir(self, job: ComponentJob) -> Path:
        work_dir = self.component_work_dir(job.component)
        return work_dir / f"build{job.target.suffix}"

    def component_output_dir(self, component: Component) -> Path:
        return self.output_dir / component.info.name

    def component_job_output_dir(self, job: ComponentJob) -> Path:
        target = job.target
        output_dir = self.component_output_dir(job.component)
        if target.is_default():
            return output_dir
        return output_dir / job.target.info.name2
