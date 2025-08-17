from collections import defaultdict
from typing import Any, Mapping, NotRequired, TypedDict, cast

from Component.ComponentFunctions import component_function
from Domain.Domains import get_domain_from_module
from Serializer.Serializer import SerializerCreator
from Utilities.File import FakeFile, File
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

description_typed_dict = TypedDict("description_typed_dict", {
    "identifier": str,
    "texture_height": NotRequired[Any],
    "texture_width": NotRequired[Any],
    "textureheight": NotRequired[Any],
    "texturewidth": NotRequired[Any],
    "visible_bounds_height": NotRequired[Any],
    "visible_bounds_offset": NotRequired[Any],
    "visible_bounds_width": NotRequired[Any],
})

geometry_typed_dict = TypedDict("geometry_typed_dict", {
    "description": description_typed_dict,
    "bones": NotRequired[dict[str,Any]]
})

model_file_type1 = TypedDict("model_file_type1", {"minecraft:geometry": list[geometry_typed_dict], "format_version": str})

model2_model_typed_dict = TypedDict("model2_model_typed_dict", {
    "description": "model2_model_typed_dict", # so it doesn't yell at me when I assign this key
    "identifier": str,
    "bones": NotRequired[dict[str,Any]],
    "texture_height": NotRequired[Any],
    "texture_width": NotRequired[Any],
    "textureheight": NotRequired[Any],
    "texturewidth": NotRequired[Any],
    "visible_bounds_height": NotRequired[Any],
    "visible_bounds_offset": NotRequired[Any],
    "visible_bounds_width": NotRequired[Any],
})

model_file_type2 = dict[str,model2_model_typed_dict]

output_typed_dict = TypedDict("output_typed_dict", {"minecraft:geometry": geometry_typed_dict, "format_version": str})

domain = get_domain_from_module(__name__)

@component_function(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("serializer", True, SerializerCreator),
))
def models_model_normalize(data:Mapping[str,Mapping[str,File[model_file_type1|model_file_type2]]], serializer:SerializerCreator) -> FakeFile[dict[str,dict[str,output_typed_dict]]]:
    output:dict[str,dict[str,output_typed_dict]] = defaultdict(lambda: {})
    file_hashes:list[int] = []
    for model_file_name, resource_packs in data.items():
        for resource_pack_name, model_file in resource_packs.items():
            file_hashes.append(hash(model_file))
            model_file_data = model_file.read(serializer.serializer)
            if "minecraft:geometry" in model_file_data:
                model_file_data = cast(model_file_type1, model_file_data)
                format_version = model_file_data["format_version"]
                for geometry_item in model_file_data["minecraft:geometry"]:
                    name = geometry_item["description"]["identifier"]
                    model_output_name = f"{model_file_name} {name}"
                    output[model_output_name][resource_pack_name] = {
                        "format_version": format_version,
                        "minecraft:geometry": geometry_item,
                    }
            else:
                format_version = cast(str, model_file_data.get("format_version"))
                for name, model_data in model_file_data.items():
                    if name == "format_version": continue
                    description:description_typed_dict = {
                        "identifier": name,
                    }
                    model_output_name = f"{model_file_name} {name}"
                    for description_key in [key for key in model_data.keys() if key != "bones"]:
                        description[description_key] = model_data[description_key]
                    if "bones" in model_data:
                        model_geometry_data:geometry_typed_dict = {"description": description, "bones": model_data["bones"]}
                    else:
                        model_geometry_data:geometry_typed_dict = {"description": description}
                    model_geometry_data["description"] = description
                    output[model_output_name][resource_pack_name] = {
                        "format_version": format_version,
                        "minecraft:geometry": model_geometry_data,
                    }
    return FakeFile("combined_models_file", output, None, hash(tuple(file_hashes)))
