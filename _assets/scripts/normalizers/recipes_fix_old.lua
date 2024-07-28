local recipe_types = {
    ["crafting_shaped"] = "minecraft:recipe_shaped",
    ["crafting_shapeless"] = "minecraft:recipe_shapeless",
    ["furnace_recipe"] = "minecraft:recipe_furnace",
}

return function (data)
    local data_attr = python.as_attrgetter(data)
    if not data_attr.__contains__("type") then
        return
    end
    --- @type string
    local old_recipe_type = data["type"]
    local new_recipe_type = recipe_types[old_recipe_type]
    if new_recipe_type == nil then
        error("Recipe type \"" .. old_recipe_type .. "\" not recognized!")
    end
    local output = python.builtins.dict()
    output[new_recipe_type] = data
    output["defined_in"] = data["defined_in"]
    data_attr.__delitem__("defined_in")
    data_attr.__delitem__("type")
    return output
end