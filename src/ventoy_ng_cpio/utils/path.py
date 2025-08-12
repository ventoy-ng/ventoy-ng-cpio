import os
from pathlib import Path
from typing import TypeAlias

PathLike: TypeAlias = str | os.PathLike[str]


def pathlike_to_path(pathlike: PathLike) -> Path:
    if any([
        isinstance(pathlike, str),
        isinstance(pathlike, os.PathLike),
    ]):
        return Path(pathlike)
    else:
        raise TypeError("{} doesn't seem Path-like".format(
            type(pathlike),
        ))
