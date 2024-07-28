return function (data)
    local output = python.builtins.dict()
    local output_attr = python.as_attrgetter(output)
    local data_attr = python.as_attrgetter(data)
    for index1, key_value1 in python.enumerate(data_attr.items()) do
        local resource_pack = key_value1[0]
        local textures = key_value1[1]
        for index, texture in python.enumerate(textures) do
            if not output_attr.__contains__(texture) then
                output[texture] = python.builtins.list()
            end
            python.as_attrgetter(output[texture]).append(resource_pack)
        end
    end
    return output
end