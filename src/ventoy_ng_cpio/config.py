from dataclasses import dataclass, field


@dataclass
class Config:
    cleanbuild: bool = field(default=False)
    c_flags: list[str] = field(default_factory=list)
    c_opt_level: str = field(default="z")
    c_lto: bool = field(default=True)


CONFIG = Config()
