from collections import defaultdict
from typing import Any, NotRequired, Required, Sequence, TypedDict, cast

from Component.ComponentFunctions import component_function
from Domain.Domains import get_domain_from_module
from Serializer.Serializer import Serializer
from Structure.SimpleContainer import SCon
from Utilities.File import FakeFile, File
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)

domain = get_domain_from_module(__name__)
json_serializer = domain.script_referenceable.get_future("minecraft_common!serializers/json", Serializer)
lines_serializer = domain.script_referenceable.get_future("minecraft_bedrock!serializers/lines_serializer", Serializer)

animation_controllers_fix_old_input_typed_dict = dict[str,Any]
animation_controllers_fix_old_output_typed_dict = TypedDict("animation_controllers_fix_old_output_typed_dict", {"animation_controllers": Any})

@component_function(no_arguments=True)
def animation_controllers_fix_old(data:animation_controllers_fix_old_input_typed_dict|animation_controllers_fix_old_output_typed_dict) -> animation_controllers_fix_old_output_typed_dict|None:
    if "animation_controllers" in data:
        return None
    output:animation_controllers_fix_old_output_typed_dict = {"animation_controllers": data}
    return output

animations_fix_old_input_typed_dict = dict[str,Any]
animations_fix_old_output_typed_dict = TypedDict("animations_fix_old_output_typed_dict", {"animations": Any})

@component_function(no_arguments=True)
def animations_fix_old(data:animations_fix_old_input_typed_dict|animations_fix_old_output_typed_dict) -> animations_fix_old_output_typed_dict|None:
    if "animations" in data:
        return None
    output:animations_fix_old_output_typed_dict = {"animations": data}
    return output

attachables_normalize_old_input_description_typed_dict = TypedDict("attachables_normalize_old_input_description_typed_dict", {
    "item": Any,
    "animations": Any,
    "geometry": Any,
    "materials": Any,
    "render_controllers": Any,
    "scripts": Any,
    "textures": Any,
})

attachables_normalize_old_input_typed_dict = dict[str,attachables_normalize_old_input_description_typed_dict]

attachables_normalize_old_output_description_typed_dict = TypedDict("attachables_normalize_old_output_description_typed_dict", {
    "identifier": NotRequired[str],
    "item": Any,
    "animations": Any,
    "geometry": Any,
    "materials": Any,
    "render_controllers": Any,
    "scripts": Any,
    "textures": Any,
})

attachables_normalize_old_output_attachable_typed_dict = TypedDict("attachables_normalize_old_output_attachable_typed_dict", {"description": attachables_normalize_old_output_description_typed_dict})

attachables_normalize_old_output_typed_dict = TypedDict("attachables_normalize_old_output_typed_dict", {"minecraft:attachable": attachables_normalize_old_output_attachable_typed_dict})

@component_function(no_arguments=True)
def attachables_normalize_old(data:attachables_normalize_old_input_typed_dict|attachables_normalize_old_output_typed_dict) -> attachables_normalize_old_output_typed_dict|None:
    if "minecraft:attachable" in data:
        return None
    attachable_identifier = list(data.keys())[0]
    output:attachables_normalize_old_output_typed_dict = {"minecraft:attachable": {"description": data[attachable_identifier]}} # type: ignore
    output["minecraft:attachable"]["description"]["identifier"] = attachable_identifier
    return output

biomes_normalize_old_input_biome_typed_dict = TypedDict("biomes_normalize_old_input_biome_typed_dict", {
    "format_version": str,
})

biomes_normalize_old_input_typed_dict = dict[str,biomes_normalize_old_input_biome_typed_dict]

biomes_normalize_old_output_description_typed_dict = TypedDict("biomes_normalize_old_output_description_typed_dict", {
    "identifier": str,
})

biomes_normalize_old_output_biome_typed_dict = TypedDict("biomes_normalize_old_output_biome_typed_dict", {
    "components": Any,
    "description": biomes_normalize_old_output_description_typed_dict,
})

biomes_normalize_old_output_typed_dict = TypedDict("biomes_normalize_old_output_typed_dict", {
    "format_version": str,
    "minecraft:biome": biomes_normalize_old_output_biome_typed_dict,
})

@component_function(no_arguments=True)
def biomes_normalize_old(data:biomes_normalize_old_input_typed_dict|biomes_normalize_old_output_typed_dict) -> biomes_normalize_old_output_typed_dict|None:
    if "minecraft:biome" in data:
        return None
    biome_identifier = list(data.keys())[0]
    output:biomes_normalize_old_output_typed_dict = {
        "format_version": data[biome_identifier]["format_version"],
        "minecraft:biome": {
            "components": data[biome_identifier],
            "description": {
                "identifier": biome_identifier
            }
        }
    }
    del output["minecraft:biome"]["components"]["format_version"]
    return output

@component_function(no_arguments=True)
def blocks_client_normalize(data:dict[str,File[dict[str,Any]]]) -> FakeFile[dict[str,dict[str,Any]]]:
    output:dict[str,dict[str,Any]] = {}
    file_hashes:list[int] = []
    for pack_name, blocks in data.items():
        file_hashes.append(blocks.hash)
        for block_name, block_data in blocks.read(json_serializer.get()).items():
            if block_name == "format_version": continue
            if block_name not in output:
                output[block_name] = {}
            output[block_name][pack_name] = block_data
    combined_hash = hash(tuple(file_hashes))
    return FakeFile("combined_blocks_file", output, None, combined_hash)

@component_function(no_arguments=True)
def categories_normalize(data:dict[str,dict[str,str]]) -> dict[str,dict[str,dict[str,str]]]:
    output:dict[str,dict[str,dict[str,str]]] = {}
    for element_name, element in data.items():
        output[element_name] = {element["type"]: element}
    return output

class FormatStringTypedDict(TypedDict):
    format: Required[str]
    color: NotRequired[str]
    should_show: NotRequired[dict[Any,Any]]
    params_to_use: NotRequired[list[Any]]

@component_function(no_arguments=True)
def commands_normalize_format_string(data:str|FormatStringTypedDict) -> FormatStringTypedDict|None:
    if isinstance(data, dict):
        return None
    else:
        return {"format": data}

@component_function(no_arguments=True)
def delete_variants_if_empty(data:dict[str,Any]) -> None:
    if "variants" in data and len(data["variants"]["key"]) == 0 and len(data["variants"]["map"]) == 0:
        del data["variants"]

entities_client_fix_old_input_type = dict[str,Any]

entities_client_fix_old_output_client_entity_typed_dict = TypedDict("entities_client_fix_old_output_client_entity_typed_dict", {
    "description": Any,
})

entities_client_fix_old_output_type = TypedDict("entities_client_fix_old_output_type", {
    "minecraft:client_entity": entities_client_fix_old_output_client_entity_typed_dict,
})

@component_function(no_arguments=True)
def entities_client_fix_old(data:entities_client_fix_old_input_type|entities_client_fix_old_output_type) -> entities_client_fix_old_output_type|None:
    if "minecraft:client_entity" in data:
        return None
    client_entity_identifier = list(data.keys())[0]
    output:entities_client_fix_old_output_type = {
        "minecraft:client_entity": {
            "description": data[client_entity_identifier]
        }
    }
    return output

item_textures_data_typed_dict = TypedDict("item_textures_data_typed_dict", {"texture_data": dict[str,Any]})

@component_function(no_arguments=True)
def item_textures_normalize(data:dict[str,File[item_textures_data_typed_dict]]) -> FakeFile[dict[str,dict[str,Any]]]:
    output:dict[str,dict[str,Any]] = {}
    file_hashes:list[int] = []
    for resource_pack_name, item_textures_file in data.items():
        file_hashes.append(hash(item_textures_file))
        item_textures_data = item_textures_file.read(json_serializer.get())
        for item, item_data in item_textures_data["texture_data"].items():
            if item not in output:
                output[item] = {}
            output[item][resource_pack_name] = item_data
    return FakeFile("combined_item_textures_file", output, None, hash(tuple(file_hashes)))

class ItemClientOffsetItemTypedDict(TypedDict):
    VR_hand_controller_position_adjust: Required[list[float]]
    VR_hand_controller_rotation_adjust: Required[list[float]]
    VR_hand_controller_scale: Required[float]

class ItemClientOffsetFileTypedDict(TypedDict):
    render_offsets: Required[dict[str,ItemClientOffsetItemTypedDict]]

@component_function(no_arguments=True)
def items_client_offset_normalize(data:dict[str,File[ItemClientOffsetFileTypedDict]]) -> FakeFile[dict[str,dict[str,ItemClientOffsetItemTypedDict]]]:
    output:dict[str,dict[str,ItemClientOffsetItemTypedDict]] = {}
    file_hashes:list[int] = []
    for resource_pack_name, file in data.items():
        file_data = file.read(json_serializer.get())
        file_hashes.append(hash(file))
        output[resource_pack_name] = file_data["render_offsets"]
    return FakeFile("combined_items_client_offset_file", output, None, hash(tuple(file_hashes)))

@component_function(no_arguments=True)
def language_names_normalize(data:list[list[str]]) -> dict[str,str]:
    return dict(data)

materials_normalize_material_input_typed_dict = TypedDict("materials_normalize_material_input_typed_dict", {"version": str, "materials": dict[str,Any]})

materials_normalize_material_output_typed_dict = TypedDict("materials_normalize_material_output_typed_dict", {"materials": dict[str,Any]})

@component_function(no_arguments=True)
def materials_normalize_material(data:materials_normalize_material_input_typed_dict|dict[str,Any]) -> materials_normalize_material_output_typed_dict|None:
    if "materials" in data:
        data["version"] = cast(str, data["materials"]["version"])
        del data["materials"]["version"]
    else:
        return {"materials": data}

@component_function(no_arguments=True)
def models_file_similarity_weight(data:str) -> Sequence[int]:
    # example string: "entity/mobs_v1.0.json geometry.humanoid.customSlim:geometry.humanoid"
    output:list[int] = [0] * len(data)
    slash_index = data.rfind("/")
    space_index = data.find(" ", max(slash_index, 0))
    if slash_index != -1:
        for i in range(slash_index):
            output[i] = 2 if i == 0 else 1
    file_extension_index = data.rfind(".", max(slash_index, 0), space_index)
    assert file_extension_index < space_index and file_extension_index != -1
    for i in range((file_extension_maximum := max(slash_index, 0)), file_extension_index):
        output[i] = 7 if i == file_extension_maximum else 3
    colon_index = data.rfind(":", space_index)
    if colon_index != -1:
        post_colon_items = data[colon_index + 1:].split(".")
        string_index = colon_index + 1
        for item in post_colon_items:
            if item != "geometry":
                for i in range(string_index, string_index + len(item)):
                    output[i] = 18 if i == string_index else 12
            string_index += len(item) + 1
    pre_colon_items = (data[space_index + 1:colon_index] if colon_index != -1 else data[space_index + 1:]).split(".")
    string_index = space_index + 1
    for item in pre_colon_items:
        if item != "geometry":
            for i in range(string_index, string_index + len(item)):
                output[i] = 15 if i == string_index else 10
        string_index += len(item) + 1
    return output

@component_function(no_arguments=True)
def music_definitions_normalize(data:dict[str,File[dict[str,Any]]]) -> FakeFile[dict[str,dict[str,Any]]]:
    output:dict[str,dict[str,Any]] = {}
    file_hashes:list[int] = []
    for pack_name, music_definitions_file in data.items():
        music_definitions = music_definitions_file.read(json_serializer.get())
        file_hashes.append(hash(music_definitions_file))
        for environment_name, environment_data in music_definitions.items():
            if environment_name not in output:
                output[environment_name] = {}
            output[environment_name][pack_name] = environment_data
    return FakeFile("combined_music_definitions_file", output, None, hash(tuple(file_hashes)))

@component_function(no_arguments=True)
def normalize_sound_definitions(data:dict[str,File[dict[str,Any]]]) -> FakeFile[dict[str,dict[str,Any]]]:
    # resource packs are always the top level.
    # inside resource pack, it's sometimes wrapped in {"sound_definitions": dict_of_sound_events}
    output:dict[str,dict[str,Any]] = {}
    file_hashes:list[int] = []
    for pack_name, sound_definitions_file in data.items():
        file_hashes.append(hash(sound_definitions_file))
        sound_definitions = sound_definitions_file.read(json_serializer.get())
        if "sound_definitions" in sound_definitions:
            sound_definitions:dict[str,Any] = sound_definitions["sound_definitions"]
        for event_name, event_data in sound_definitions.items():
            if event_name not in output:
                output[event_name] = {}
            output[event_name][pack_name] = event_data
    return FakeFile("combined_sound_definitions_file", output, None, hash(tuple(file_hashes)))

@component_function(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("serializer", True, str),
))
def open_file[A](data:A|File[A], serializer:str) -> A|None:
    if isinstance(data, File):
        return data.read(domain.script_referenceable.get(serializer))

packs_normalize_pack_typed_dict = TypedDict("packs_normalize_pack_typed_dict", {"path": str, "name": str})

@component_function(no_arguments=True)
def packs_normalize(data:list[packs_normalize_pack_typed_dict]) -> list[str]:
    return [pack["name"] for pack in data]

@component_function(no_arguments=True)
def particles_normalize_component_particle_appearance_tinting_color(data:dict|str|list) -> list|dict|None:
    if isinstance(data, (str, list)):
        return [data]

particles_normalize_old_description_typed_dict = TypedDict("particles_normalize_old_description_typed_dict", {
    "basic_render_parameters": dict[str,Any],
    "identifier": str,
})

particles_normalize_old_particle_effect_typed_dict = TypedDict("particles_normalize_old_particle_effect_typed_dict", {
    "description": particles_normalize_old_description_typed_dict,
})

particles_normalize_old_output_type = TypedDict("particles_normalize_old_output_type", {
    "format_version": str,
    "particle_effect": particles_normalize_old_particle_effect_typed_dict,
})

particles_normalize_old_input_type = dict[str,Any]

@component_function(no_arguments=True)
def particles_normalize_old(data:particles_normalize_old_input_type|particles_normalize_old_output_type) -> particles_normalize_old_output_type|None:
    if "particles" not in data:
        return
    particle_identifier = list(data["particles"].keys())[0] # type: ignore
    output:particles_normalize_old_output_type = {
        "format_version": cast(str, data["format_version"]),
        "particle_effect": data["particles"][particle_identifier], # type: ignore
    }
    output["particle_effect"]["description"] = {
        "basic_render_parameters": data["particles"][particle_identifier]["basic_render_parameters"], # type: ignore
        "identifier": particle_identifier,
    }
    del output["particle_effect"]["basic_render_parameters"] # type: ignore
    return output

@component_function(no_arguments=True)
def pieces_normalize(data:list[str]) -> list[str]:
    data = list(set(data)) # deduplicate
    data = list(filter(lambda item: "." not in item, data))
    return data

recipes_fix_old_recipe_types = {
    "crafting_shaped": "minecraft:recipe_shaped",
    "crafting_shapeless": "minecraft:recipe_shapeless",
    "furnace_recipe": "minecraft:recipe_furnace",
}

@component_function(no_arguments=True)
def recipes_fix_old(data:dict[str,Any]) -> dict[str,dict[str,Any]]|None:
    if "type" not in data:
        return None
    new_recipe_type = recipes_fix_old_recipe_types[data["type"]]
    output = {new_recipe_type: data}
    data.pop("defined_in", None)
    del data["type"]
    return output

@component_function(no_arguments=True)
def remove_minecraft_prefix(data:SCon[str]) -> str:
    return data.data.removeprefix("minecraft:")

@component_function(no_arguments=True)
def remove_file_suffix(data:SCon[str]) -> str:
    split_data = data.data.split(".")
    # some file names are like "donkey.v1.2.6.entity.json"; I want to include the v1.2.6.
    if len(indexes := [index for index, item in enumerate(split_data) if item.isdigit()]) > 0:
        return ".".join(split_data[:indexes[-1] + 1])
    elif len(split_data[0]) == 0:
        return ".".join(split_data)
    else:
        return split_data[0]

@component_function(no_arguments=True)
def render_controllers_fix_old(data:Any) -> Any|None:
    if "render_controllers" in data:
        return None
    output = {"render_controllers": data}
    return output

@component_function(no_arguments=True)
def renderer_options_dragon_normalize(data:list[list[str]]) -> dict[str,str]:
    return dict(data) # iterable of iterables with two items each

@component_function(no_arguments=True)
def renderer_options_normalize_mappings(data:dict[str,list[Any]]|list[Any]) -> dict[str,list[Any]]|None:
    if isinstance(data, list):
        return {"mappings": data}

@component_function(no_arguments=True)
def renderer_platform_configurations_normalize_shadow_config(data:Any) -> Any|None:
    if "file" in data:
        return {"shadow_config": data}

class SkinsNormalizeInputTypedDict(TypedDict):
    skins: list[dict[str,Any]]

class SkinsNormalizeOutputTypedDict(TypedDict):
    skins: list[dict[str,Any]]

@component_function(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("other_keys", True, ListTypeVerifier(str, list)),
))
def skins_normalize(data:dict[str,File[SkinsNormalizeInputTypedDict]], other_keys:list[str]) -> FakeFile[SkinsNormalizeOutputTypedDict]:
    output:SkinsNormalizeOutputTypedDict = {
        "skins": [],
    }
    for other_key in other_keys:
        output[other_key] = {}
    file_hashes:list[int] = []
    for pack_name, skins_file in data.items():
        file_hashes.append(hash(skins_file))
        skins_data = skins_file.read(json_serializer.get())
        for skin in skins_data["skins"]:
            skin["defined_in"] = pack_name
            output["skins"].append(skin)
        for other_key in other_keys:
            output[other_key][pack_name] = skins_data[other_key]
    return FakeFile("combined_skins_file", output, None, hash(tuple(file_hashes)))

@component_function(no_arguments=True)
def sound_definitions_make_strings_to_dict(data:Any) -> Any:
    if isinstance(data, str):
        return {"name": data}

# default is 12
SPECIAL_WEIGHTS = [
    {
        "mob": 6,
        "block": 5,
        "step": 5,
        "hit": 5,
        "fall": 5,
        "use": 5,
        "jump": 5,
        "land": 5,
        "break": 5,
        "place": 5,
        "random": 6,
        "dig": 5,
        "music": 6,
        "ambient": 3,
        "item": 4,
    },
    {
        "game": 6,
    },
    {
        "hurt": 9,
        "step": 9,
        "death": 9,
        "ambient": 9,
        "idle": 9,
        "hit": 9,
        "break": 6,
        "place": 6,
        "say": 9,
        "eat": 9,
        "fall": 6,
        "use": 9,
        "attack": 9,
        "0": 24, "1": 24, "2": 24, "3": 24, "4": 24, "5": 24, "6": 24, "7": 24, "8": 24, "9": 24,
    },
    {
        "hit": 9,
        "death": 9,
        "idle": 9,
    },
]

@component_function(no_arguments=True)
def sound_events_similarity_weight(data:str) -> list[int]:
    items = data.split(".")
    string_index = 0
    weights:list[int] = [1] * len(data)
    for index, item in enumerate(items):
        for i in range(string_index, string_index + len(item)):
            weights[i] = SPECIAL_WEIGHTS[index].get(item, 12) * (index + 2) // 2
        string_index += len(item) + 1
    return weights

@component_function(no_arguments=True)
def sounds_json_make_strings_to_dict(data:Any) -> Any:
    if isinstance(data, str):
        return {"sound": data}

@component_function(no_arguments=True)
def spawn_rules_normalize_herd(data:dict[str,Any]|list[dict[str,Any]]) -> list[dict[str,Any]]|None:
    if isinstance(data, dict):
        return [data]

@component_function(no_arguments=True)
def subdirs_normalize(data:dict[str,File[list[str]]]) -> list[str]:
    output:list[str] = []
    for file_name, file in data.items():
        file_contents = file.read(lines_serializer.get())
        file_name_stripped = file_name.rsplit("/", 1)[0] + "/"
        for line in file_contents:
            output.append(file_name_stripped + line)
    return output

@component_function(no_arguments=True)
def terrain_textures_normalize(data:dict[str,File[dict[str,Any]]]) -> FakeFile[dict[str,dict[str,Any]]]:
    other_keys = {"texture_name": {}, "padding": {}, "num_mip_levels": {}}
    texture_data:dict[str,dict[str,Any]] = {}
    file_hashes:list[int] = []
    for resource_pack_name, terrain_textures_file in data.items():
        terrain_textures_data = terrain_textures_file.read(json_serializer.get())
        file_hashes.append(hash(terrain_textures_file))
        for other_key_key, other_key_values in other_keys.items():
            if other_key_key in terrain_textures_data:
                other_key_values[resource_pack_name] = terrain_textures_data[other_key_key]
        for terrain, terrain_data in terrain_textures_data["texture_data"].items():
            if terrain not in texture_data:
                texture_data[terrain] = {}
            texture_data[terrain][resource_pack_name] = terrain_data
    output = other_keys
    output["texture_data"] = texture_data
    return FakeFile("combined_terrain_textures_file", output, None, hash(tuple(file_hashes)))

@component_function(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("serializer", True, str),
))
def texture_list_normalize(data:dict[str,File[list[str]]], serializer:str) -> FakeFile[dict[str,list[str]]]:
    _serializer = domain.script_referenceable.get(serializer, Serializer)
    output:defaultdict[str,list[str]] = defaultdict(lambda: [])
    file_hashes:list[int] = []
    for resource_pack, textures_file in data.items():
        textures = textures_file.read(_serializer)
        file_hashes.append(hash(textures_file))
        for texture in textures:
            output[texture].append(resource_pack)
    return FakeFile("combined_texture_list_file", dict(output), None, hash(tuple(file_hashes)))

@component_function(no_arguments=True)
def textures_split_lines(data:list[str]|str) -> list[str]|None:
    if isinstance(data, str):
        return data.splitlines()

@component_function(no_arguments=True)
def tiers_bin_normalize_gpu(data:int|dict) -> dict|None:
    if isinstance(data, int):
        return {"tier": data}

@component_function(no_arguments=True)
def ui_separate_variables(data:dict[str,Any]) -> None:
    variables:dict[str,Any] = {}
    for parameter_name, parameter_value in data.items():
        if parameter_name.startswith("$"):
            variables[parameter_name] = parameter_value
    for variable_name in variables.keys():
        del data[variable_name] # variables are not wanted in the element afterward
    assert "$variables" not in data
    if len(variables) > 0:
        data["$variables"] = variables

@component_function(no_arguments=True)
def uniforms_normalize(data:dict[str,str]) -> dict[str,str]|None:
    if "Name" in data:
        return
    assert len(data) == 1
    key = list(data.keys())[0]
    value = data[key]
    return {"Name": key, "Type": value}
