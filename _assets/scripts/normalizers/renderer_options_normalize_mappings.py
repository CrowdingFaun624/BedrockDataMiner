from typing import Any

__all__ = ["renderer_options_normalize_mappings"]

def renderer_options_normalize_mappings(data:dict[str,list[Any]]|list[Any]) -> dict[str,list[Any]]|None:
    if isinstance(data, list):
        return {"mappings": data}