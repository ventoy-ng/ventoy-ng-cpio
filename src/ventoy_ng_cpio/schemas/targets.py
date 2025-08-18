from dataclasses import dataclass, field
from typing import Any, Optional

from mashumaro.mixins.toml import DataClassTOMLMixin


@dataclass(frozen=True)
class TargetTriplet(DataClassTOMLMixin):
    machine: str
    vendor: Optional[str] = field(default=None)
    operatingsystem: Optional[str] = field(default=None)
    extras: Optional[dict[str, Any]] = field(default=None)

    @property
    def arch(self) -> str:
        return self.machine

    def get_vendor(self, default: Optional[str] = None) -> str:
        if self.vendor is not None:
            return self.vendor
        if default is not None:
            return default
        return "unknown"

    def get_libc(self) -> str:
        assert self.operatingsystem == "linux"
        assert self.extras
        libc = self.extras["libc"]
        assert isinstance(libc, str)
        return libc

    def to_string(
        self,
        default_vendor: Optional[str] = None,
        default_os: Optional[str] = None,
    ) -> str:
        res = self.machine
        assert self.operatingsystem == "linux"
        res += "-" + self.get_vendor(default=default_vendor)
        res += "-" + self.operatingsystem
        res += "-" + self.get_libc()
        return res


@dataclass(frozen=True)
class TargetInfo(DataClassTOMLMixin):
    """
    name examples:
    - system/i386
    - system/x86_64
    - output/x86
    """
    name: str
    suffix: Optional[str] = field(default=None)
    triplet: Optional[TargetTriplet] = field(default=None)
    subtargets: Optional[list[str]] = field(default=None)
    virtual: bool = field(default=False)

    @property
    def name2(self) -> str:
        return self.name.split("/")[1]

    def get_triplet(self) -> TargetTriplet:
        if self.triplet is None:
            raise ValueError
        return self.triplet

    @property
    def arch(self) -> str:
        return self.get_triplet().arch

    def get_cross(
        self,
        default_vendor: Optional[str] = None,
        default_os: Optional[str] = None,
    ) -> str:
        triplet = self.get_triplet().to_string(
            default_vendor=default_vendor,
            default_os=default_os,
        )
        return triplet + "-"
