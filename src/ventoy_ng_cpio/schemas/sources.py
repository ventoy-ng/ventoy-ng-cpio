from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import ParseResult, urlparse

from mashumaro import field_options
from mashumaro.mixins.toml import DataClassTOMLMixin


@dataclass(frozen=True)
class SourceInfo(DataClassTOMLMixin):
    name: str
    raw_id: str = field(
        metadata=field_options(
            alias="id",
        ),
    )
    version: Optional[str] = field(default=None)
    url: Optional[str] = field(default=None)
    filename: Optional[str] = field(default=None)
    xhash: Optional[str] = field(
        default=None,
        metadata=field_options(
            alias="hash",
        ),
    )
    extracted_name: Optional[str] = field(default=None)
    submod: bool = field(default=False)

    def get_id(self) -> str:
        return self.raw_id.format(
            name=self.name,
            version=self.version,
        )

    def get_url(self) -> Optional[str]:
        url = self.url
        if url is None:
            return None
        return url.format(
            name=self.name,
            version=self.version,
        )

    def get_url_obj(self) -> Optional[ParseResult]:
        url_str = self.get_url()
        if url_str is None:
            return None
        url = urlparse(url_str)
        assert isinstance(url, ParseResult)
        return url

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

    def get_extracted_name(self) -> str:
        extracted_name = self.extracted_name
        assert extracted_name is not None
        return extracted_name.format(
            name=self.name,
            version=self.version,
        )
