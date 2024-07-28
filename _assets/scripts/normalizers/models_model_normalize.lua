return function (data)
    local data_attr = python.as_attrgetter(data)
    local output = python.builtins.dict()
    local output_attr = python.as_attrgetter(output)
    for index1, key_value1 in python.enumerate(data_attr.items()) do
        local model_file_name = key_value1[0]
        local resource_packs = key_value1[1]
        local resource_packs_attr = python.as_attrgetter(resource_packs)
        for index2, key_value2 in python.enumerate(resource_packs_attr.items()) do
            local resource_pack_name = key_value2[0]
            local model_file_data = key_value2[1]
            local model_file_data_attr = python.as_attrgetter(model_file_data)
            if model_file_data_attr.__contains__("minecraft:geometry") then
                local format_version = model_file_data["format_version"]
                assert(python.builtins.type(model_file_data["minecraft:geometry"] == python.builtins.list))
                for index3, geometry_item in python.enumerate(model_file_data["minecraft:geometry"]) do
                    local name = geometry_item["description"]["identifier"]
                    local model_output_name = model_file_name .. " " .. name
                    if not output_attr.__contains__(model_output_name) then
                        output[model_output_name] = python.builtins.dict()
                    end
                    output[model_output_name][resource_pack_name] = python.builtins.dict()
                    output[model_output_name][resource_pack_name]["format_version"] = format_version
                    output[model_output_name][resource_pack_name]["minecraft:geometry"] = geometry_item
                end
            else
                local format_version = model_file_data_attr.get("format_version")
                for index3, key_value3 in python.enumerate(model_file_data_attr.items()) do
                    local name = key_value3[0]
                    local model_data = key_value3[1]
                    if name ~= "format_version" then
                        local model_data_attr = python.as_attrgetter(model_data)
                        local description_dict = python.builtins.dict()
                        description_dict["identifier"] = name
                        local model_output_name = model_file_name .. " " .. name
                        local keys = {}
                        for index4, description_key in python.enumerate(model_data_attr.keys()) do
                            if description_key ~= "bones" then
                                table.insert(keys, description_key)
                            end
                        end
                        -- split into two for statements because dicts can't have keys deleted while iterating.
                        for index4, description_key in pairs(keys) do
                            description_dict[description_key] = model_data[description_key]
                            model_data_attr.__delitem__(description_key)
                        end
                        model_data["description"] = description_dict
                        if not output_attr.__contains__(model_output_name) then
                            output[model_output_name] = python.builtins.dict()
                        end
                        output[model_output_name][resource_pack_name] = python.builtins.dict()
                        output[model_output_name][resource_pack_name]["format_version"] = format_version
                        output[model_output_name][resource_pack_name]["minecraft:geometry"] = model_data
                    end
                end
            end
        end
    end
    return output
end