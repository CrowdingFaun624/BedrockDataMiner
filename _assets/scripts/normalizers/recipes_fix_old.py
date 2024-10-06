from typing import Any

__all__ = ["recipes_fix_old"]

recipe_types = {
    "crafting_shaped": "minecraft:recipe_shaped",
    "crafting_shapeless": "minecraft:recipe_shapeless",
    "furnace_recipe": "minecraft:recipe_furnace",
}

def recipes_fix_old(data:dict[str,Any]) -> dict[str,dict[str,Any]]|None:
    if "type" not in data:
        return None
    new_recipe_type = recipe_types[data["type"]]
    output = {new_recipe_type: data}
    data.pop("defined_in", None)
    del data["type"]
    return output
