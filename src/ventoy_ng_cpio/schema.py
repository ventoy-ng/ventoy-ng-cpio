from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional
from urllib.parse import ParseResult, urlparse

from mashumaro import field_options
from mashumaro.mixins.toml import DataClassTOMLMixin


@dataclass(frozen=True)
class TargetInfo(DataClassTOMLMixin):
    """
    name examples:
    - system/i386
    - system/x86_64
    - output/x86
    """
    name: str
    triplet: Optional[str] = field(default=None)
    suffix: Optional[str] = field(default=None)
    use_suffix: bool = field(default=True)
    subtargets: Optional[list[str]] = field(default=None)

    @property
    def arch(self) -> str:
        assert self.triplet
        return self.triplet.split("-")[0]

    @property
    def name2(self) -> str:
        return self.name.split("/")[1]


@dataclass(frozen=True)
class SourceInfo(DataClassTOMLMixin):
    name: str
    version: str
    raw_id: str = field(metadata=field_options(
        alias="id",
    ))
    url: Optional[str] = field(default=None)
    filename: Optional[str] = field(default=None)
    xhash: Optional[str] = field(
        default=None,
        metadata=field_options(
            alias="hash",
        ),
    )
    extracted_name: Optional[str] = field(default=None)

    @lru_cache(1)
    def get_id(self) -> str:
        return self.raw_id.format(
            name=self.name,
            version=self.version,
        )

    @lru_cache(1)
    def get_url(self) -> Optional[str]:
        url = self.url
        if url is None:
            return None
        return url.format(
            name=self.name,
            version=self.version,
        )

    @lru_cache(1)
    def get_url_obj(self) -> Optional[ParseResult]:
        url_str = self.get_url()
        if url_str is None:
            return None
        url = urlparse(url_str)
        assert isinstance(url, ParseResult)
        return url

    @lru_cache(1)
    def get_filename(self) -> str:
        filename = self.filename
        if filename is not None:
            return filename.format(
                name=self.name,
                version=self.version,
            )
        url = self.get_url_obj()
        if url is not None:
            return Path(url.path).name
        raise ValueError

    @lru_cache(1)
    def get_extracted_name(self) -> str:
        extracted_name = self.extracted_name
        assert extracted_name is not None
        return extracted_name.format(
            name=self.name,
            version=self.version,
        )


@dataclass(frozen=True)
class ComponentInfo(DataClassTOMLMixin):
    name: str
    target_set: Optional[str] = field(default=None)
    sources: list[str] = field(default_factory=list)
    deps: list[str] = field(default_factory=list)
    build_file: Optional[Path] = field(default=None)
    build_args: Optional[Any] = field(default=None)


@dataclass(frozen=True)
class ProjectInfo(DataClassTOMLMixin):
    name: str
    target: list[TargetInfo]
    sources: list[SourceInfo]
    components: list[ComponentInfo]
