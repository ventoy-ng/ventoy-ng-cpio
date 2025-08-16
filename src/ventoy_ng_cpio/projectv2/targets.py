from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Self

from ..schemas.targets import TargetInfo


ARCHES_32 = ["i386"]


@dataclass(frozen=True)
class Target:
    info: TargetInfo
    subtargets: Optional[list[Self]]

    @classmethod
    def new(
        cls,
        info: TargetInfo,
        targets: Optional[dict[str, Self]] = None,
    ) -> Self:
        if info.subtargets is not None:
            if targets is None:
                raise ValueError
            subtargets = [
                targets[subtarget_name]
                for subtarget_name in info.subtargets
            ]
        else:
            subtargets = None
        this = cls(info, subtargets) # type: ignore
        assert DEFAULT_TARGET.subtargets is not None
        DEFAULT_TARGET.subtargets.append(this)
        return this

    @classmethod
    def new_for(cls, tgtinfo: dict[Path, TargetInfo]) -> dict[str, Self]:
        targets: dict[str, Self] = {}
        for info in tgtinfo.values():
            target = cls.new(info, targets)
            targets[info.name] = target
        return targets

    @classmethod
    def default(cls) -> "Target":
        return DEFAULT_TARGET

    def is_default(self) -> bool:
        return self is DEFAULT_TARGET

    @property
    def suffix(self) -> str:
        if self.is_default():
            return ""
        return f"-{self.info.name2}"

    def is_subtarget(self, other: Self) -> bool:
        if other is self:
            return True
        if not self.subtargets:
            return False
        return any([
            target.is_subtarget(other)
            for target in self.subtargets
        ])

    def get_bitness(self) -> int:
        if self.info.arch in ARCHES_32:
            return 32
        return 64

    def get_cmd(self, command: str) -> str:
        return self.info.get_cross() + command


DEFAULT_TARGET_INFO = TargetInfo(
    name="TARGETLESS",
    suffix=None,
    triplet=None,
    subtargets=None,
    virtual=True,
)
DEFAULT_TARGET = Target(
    DEFAULT_TARGET_INFO,
    subtargets=[],
)


@dataclass(frozen=True)
class TargetSet:
    name: str
    targets: list[Target]

    @classmethod
    def new_for(
        cls,
        targets: dict[str, Target],
    ) -> dict[str, Self]:
        target_sets: dict[str, list[Target]] = {}
        for tname, target in targets.items():
            tset = tname.split("/")[0]
            if tset not in target_sets:
                target_sets[tset] = []
            tseta = target_sets[tset]
            tseta.append(target)
        return {
            name: cls(name, info)
            for name, info in target_sets.items()
        }
