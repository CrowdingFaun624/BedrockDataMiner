from typing import Any, NotRequired, Required, TypedDict

__all__ = ["commands_normalize_format_string"]

class FormatStringTypedDict(TypedDict):
    format: Required[str]
    color: NotRequired[str]
    should_show: NotRequired[dict[Any,Any]]
    params_to_use: NotRequired[list[Any]]

def commands_normalize_format_string(data:str|FormatStringTypedDict) -> FormatStringTypedDict|None:
    if isinstance(data, dict):
        return None
    else:
        return {"format": data}
