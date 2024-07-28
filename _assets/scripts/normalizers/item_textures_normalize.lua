return function (data)
    local data_attr = python.as_attrgetter(data)
    local output = python.builtins.dict()
    local output_attr = python.as_attrgetter(output)
    for index, key_value in python.enumerate(data_attr.items()) do
        local resource_pack_name = key_value[0]
        local item_textures_data = key_value[1]
        local item_textures_data_attr = python.as_attrgetter(item_textures_data["texture_data"])
        for index2, key_value2 in python.enumerate(item_textures_data_attr.items()) do
            local item = key_value2[0]
            local item_data = key_value2[1]
            if not output_attr.__contains__(item) then
                output[item] = python.builtins.dict()
            end
            output[item][resource_pack_name] = item_data
        end
    end
    return output
end