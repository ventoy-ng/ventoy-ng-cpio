from abc import ABC, abstractmethod
from inspect import isabstract
from typing import ClassVar


_build_impls: dict[str, type["BaseBuilder"]] = {}


class BaseBuilder(ABC):
    name: ClassVar[str] = ""

    def __init_subclass__(cls) -> None:
        if isabstract(cls):
            return
        if not cls.name:
            raise Exception
        assert isinstance(cls.name, str)
        _build_impls[cls.name] = cls

    @abstractmethod
    def prepare(self):
        pass

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def install(self):
        pass

    @classmethod
    def get_builder(cls, name: str) -> type["BaseBuilder"]:
        builder_c = _build_impls[name]
        return builder_c
