return function (data)
    local data_attr = python.as_attrgetter(data)
    if data_attr.__contains__("minecraft:biome") then
        return
    end
    local biome_identifier = nil
    for index, key in python.enumerate(data) do
        biome_identifier = key
        break
    end
    assert(biome_identifier ~= nil, "dictionary is empty; cannot find biome identifier")
    local output = python.builtins.dict()
    output["format_version"] = data[biome_identifier]["format_version"]
    output["minecraft:biome"] = python.builtins.dict()
    output["minecraft:biome"]["components"] = data[biome_identifier]
    output["minecraft:biome"]["description"] = python.builtins.dict()
    output["minecraft:biome"]["description"]["identifier"] = biome_identifier
    python.as_attrgetter(output["minecraft:biome"]["components"]).__delitem__("format_version")
    return output
end