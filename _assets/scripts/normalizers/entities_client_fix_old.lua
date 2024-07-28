return function (data)
    local data_attr = python.as_attrgetter(data)
    if data_attr.__contains__("minecraft:client_entity") then
        return
    end
    local client_entity_identifier = nil
    for index, key in python.enumerate(data) do
        client_entity_identifier = key
        break
    end
    assert(client_entity_identifier ~= nil, "dictionary is empty; cannot find client entity identifier")
    local output = python.builtins.dict()
    output["defined_in"] = data["defined_in"]
    output["minecraft:client_entity"] = python.builtins.dict()
    output["minecraft:client_entity"]["description"] = data[client_entity_identifier]
    return output
end