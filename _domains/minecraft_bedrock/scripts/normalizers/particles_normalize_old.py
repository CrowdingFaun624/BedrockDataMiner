from typing import Any, TypedDict, cast

__all__ = ["particles_normalize_old"]

description_typed_dict = TypedDict("description_typed_dict", {
    "basic_render_parameters": dict[str,Any],
    "identifier": str,
})

particle_effect_typed_dict = TypedDict("particle_effect_typed_dict", {
    "description": description_typed_dict,
})

output_type = TypedDict("output_type", {
    "format_version": str,
    "particle_effect": particle_effect_typed_dict,
})

input_type = dict[str,Any]

def particles_normalize_old(data:input_type|output_type) -> output_type|None:
    if "particles" not in data:
        return
    particle_identifier = list(data["particles"].keys())[0]
    output:output_type = {
        "format_version": cast(str, data["format_version"]),
        "particle_effect": data["particles"][particle_identifier],
    }
    output["particle_effect"]["description"] = {
        "basic_render_parameters": data["particles"][particle_identifier]["basic_render_parameters"],
        "identifier": particle_identifier,
    }
    del output["particle_effect"]["basic_render_parameters"] # type: ignore
    return output
