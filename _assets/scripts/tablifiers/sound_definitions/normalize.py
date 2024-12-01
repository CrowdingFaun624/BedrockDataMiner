from typing import TypeVar

import Utilities.File as File

__all__ = ["normalize"]

a = TypeVar("a")

def normalize(data:dict[str,File.File[a]]) -> dict[str,a]:
    return {key: value.data for key, value in data.items()}
