from typing import Any

__all__ = ["spawn_rules_normalize_herd"]

def spawn_rules_normalize_herd(data:dict[str,Any]|list[dict[str,Any]]) -> list[dict[str,Any]]|None:
    if isinstance(data, dict):
        return [data]
