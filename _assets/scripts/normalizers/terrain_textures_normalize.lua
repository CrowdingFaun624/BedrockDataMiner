return function (data)
    local data_attr = python.as_attrgetter(data)
    local other_keys = python.builtins.dict()
    local other_keys_attr = python.as_attrgetter(other_keys)
    other_keys["texture_name"] = python.builtins.dict()
    other_keys["padding"] = python.builtins.dict()
    other_keys["num_mip_levels"] = python.builtins.dict()
    local texture_data = python.builtins.dict()
    local texture_data_attr = python.as_attrgetter(texture_data)
    for index1, key_value1 in python.enumerate(data_attr.items()) do
        local resource_pack_name = key_value1[0]
        local terrain_textures_data = key_value1[1]
        local terrain_textures_data_attr = python.as_attrgetter(terrain_textures_data)
        for index2, key_value2 in python.enumerate(other_keys_attr.items()) do
            local other_key_key = key_value2[0]
            local other_key_values = key_value2[1]
            if terrain_textures_data_attr.__contains__(other_key_key) then
                other_key_values[resource_pack_name] = terrain_textures_data[other_key_key]
            end
        end
        for index2, key_value2 in python.enumerate(python.as_attrgetter(terrain_textures_data["texture_data"]).items()) do
            local terrain = key_value2[0]
            local terrain_data = key_value2[1]
            if not texture_data_attr.__contains__(terrain) then
                texture_data[terrain] = python.builtins.dict()
            end
            texture_data[terrain][resource_pack_name] = terrain_data
        end
    end
    local output = other_keys
    output["texture_data"] = texture_data
    return output
end