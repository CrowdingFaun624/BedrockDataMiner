from typing import Any, TypedDict

__all__ = ["languages_normalize"]

language_typed_dict = TypedDict("language_typed_dict", code=str, properties=dict[str,Any], defined_in=list[str])

def fix_properties(data:language_typed_dict) -> dict[str,dict[str,Any]]:
    output:dict[str,dict[str,Any]] = data["properties"]
    output.update(
        (resource_pack, {})
        for resource_pack in data["defined_in"]
        if resource_pack not in output
    )
    return output

def languages_normalize(data:list[language_typed_dict]) -> dict[str,dict[str,dict[str,Any]]]:
    return {language["code"]: fix_properties(language) for language in data}
