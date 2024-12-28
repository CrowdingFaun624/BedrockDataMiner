from typing import Any, NotRequired, TypedDict

__all__ = ["attachables_normalize_old"]

input_description_typed_dict = TypedDict("input_description_typed_dict", {
    "item": Any,
    "animations": Any,
    "geometry": Any,
    "materials": Any,
    "render_controllers": Any,
    "scripts": Any,
    "textures": Any,
})

input_typed_dict = dict[str,input_description_typed_dict]

output_description_typed_dict = TypedDict("output_description_typed_dict", {
    "identifier": NotRequired[str],
    "item": Any,
    "animations": Any,
    "geometry": Any,
    "materials": Any,
    "render_controllers": Any,
    "scripts": Any,
    "textures": Any,
})

output_attachable_typed_dict = TypedDict("output_attachable_typed_dict", {"description": output_description_typed_dict})

output_typed_dict = TypedDict("output_typed_dict", {"minecraft:attachable": output_attachable_typed_dict})

def attachables_normalize_old(data:input_typed_dict|output_typed_dict) -> output_typed_dict|None:
    if "minecraft:attachable" in data:
        return None
    attachable_identifier = list(data.keys())[0]
    output:output_typed_dict = {"minecraft:attachable": {"description": data[attachable_identifier]}} # type: ignore
    output["minecraft:attachable"]["description"]["identifier"] = attachable_identifier
    return output
