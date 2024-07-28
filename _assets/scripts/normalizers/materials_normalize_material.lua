return function (data)
    local data_attr = python.as_attrgetter(data)
    if data_attr.__contains__("materials") then
        data["version"] = data["materials"]["version"]
    else
        local output = python.builtins.dict()
        output["materials"] = data
        output["defined_in"] = data["defined_in"]
        return output
    end
end