return function (data)
    local data_attr = python.as_attrgetter(data)
    if data_attr.__contains__("minecraft:attachable") then
        return
    end
    local attachable_identifier = nil
    for index, key in python.enumerate(data) do
        attachable_identifier = key
        break
    end
    assert(attachable_identifier ~= nil, "dictionary is empty; cannot find attachable identifier")
    local output = python.builtins.dict()
    output["minecraft:attachable"] = python.builtins.dict()
    output["minecraft:attachable"]["description"] = data[attachable_identifier]
    output["minecraft:attachable"]["description"]["identifier"] = attachable_identifier
    return output
end