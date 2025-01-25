import Utilities.File as File

__all__ = ("normalize",)

def normalize[a](data:dict[str,File.File[a]]) -> dict[str,a]:
    return {key: value.data for key, value in data.items()}
