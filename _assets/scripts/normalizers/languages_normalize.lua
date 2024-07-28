local function fix_properties(data)
    local output = data["properties"]
    local output_attr = python.as_attrgetter(output)
    for index, resource_pack in python.enumerate(data["defined_in"]) do
        if not output_attr.__contains__(resource_pack) then
            output[resource_pack] = python.builtins.dict()
        end
    end
    return output
end

return function (data)
    local output = python.builtins.dict()
    for index, language in python.enumerate(data) do
        output[language["code"]] = fix_properties(language)
    end
    return output
end