return function (data)
    local data_attr = python.as_attrgetter(data)
    if data_attr.__contains__("file") then
        local output = python.builtins.dict()
        output["shadow_config"] = data
        return output
    end
end