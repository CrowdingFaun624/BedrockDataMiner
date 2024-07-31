from typing import Any, TypedDict

__all__ = ["blocks_client_normalize"]

input_typed_dict = TypedDict("input_typed_dict", name=str, properties=dict[str,Any])

def blocks_client_normalize(data:list[input_typed_dict]) -> dict[str,dict[str,Any]]:
    return {block["name"]: block["properties"] for block in data}
