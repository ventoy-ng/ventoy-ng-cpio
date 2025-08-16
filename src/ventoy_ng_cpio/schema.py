from dataclasses import dataclass

from mashumaro.mixins.toml import DataClassTOMLMixin


@dataclass(frozen=False)
class ProjectInfo(DataClassTOMLMixin):
    name: str
