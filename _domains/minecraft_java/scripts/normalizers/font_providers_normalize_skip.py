__all__ = ["font_providers_normalize_skip"]


def font_providers_normalize_skip(data:str|list[str]) -> list[str]|None:
    if isinstance(data, str):
        return list(data)
