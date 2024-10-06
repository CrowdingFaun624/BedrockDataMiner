from typing import TypedDict

__all__ = ["packs_normalize"]

pack_typed_dict = TypedDict("pack_typed_dict", path=str, name=str)

def packs_normalize(data:list[pack_typed_dict]) -> list[str]:
    return [pack["name"] for pack in data]
