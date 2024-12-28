from collections import defaultdict
from typing import Any, NotRequired, TypedDict, cast

import Utilities.File as File

__all__ = ["models_model_normalize"]

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
    "bones": dict[str,Any]
})

model_file_type1 = TypedDict("model_file_type1", {"minecraft:geometry": list[geometry_typed_dict], "format_version": str})

model2_model_typed_dict = TypedDict("model2_model_typed_dict", {
    "description": NotRequired["model2_model_typed_dict"], # so it doesn't yell at me when I assign this key
    "identifier": str,
    "bones": dict[str,Any],
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

def models_model_normalize(data:dict[str,dict[str,File.File[model_file_type1|model_file_type2]]]) -> File.FakeFile[dict[str,dict[str,output_typed_dict]]]:
    output:dict[str,dict[str,output_typed_dict]] = defaultdict(lambda: {})
    file_hashes:list[int] = []
    for model_file_name, resource_packs in data.items():
        for resource_pack_name, model_file in resource_packs.items():
            file_hashes.append(hash(model_file))
            model_file_data = model_file.data
            if "minecraft:geometry" in model_file_data:
                model_file_data = cast(model_file_type1, model_file_data)
                format_version = model_file_data["format_version"]
                for geometry_item in model_file_data["minecraft:geometry"]:
                    name = geometry_item["description"]["identifier"]
                    model_output_name = "%s %s" % (model_file_name, name)
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
                    model_output_name = "%s %s" % (model_file_name, name)
                    for description_key in [key for key in model_data.keys() if key != "bones"]:
                        description[description_key] = model_data[description_key]
                        del model_data[description_key]
                    model_data = cast(geometry_typed_dict, model_data)
                    model_data["description"] = description
                    output[model_output_name][resource_pack_name] = {
                        "format_version": format_version,
                        "minecraft:geometry": model_data,
                    }
    return File.FakeFile("combined_models_file", output, hash(tuple(file_hashes)))
