from dataclasses import dataclass, field


def default_cflags() -> list[str]:
    return ["-Oz"]


@dataclass
class ProjectConfig:
    cflags: list[str] = field(default_factory=default_cflags)


@dataclass
class Config:
    cleanbuild: bool = field(default=False)
    project: ProjectConfig = field(default_factory=ProjectConfig)


CONFIG = Config()
