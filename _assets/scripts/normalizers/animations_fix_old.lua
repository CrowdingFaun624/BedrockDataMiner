return function(data)
    local data_attr = python.as_attrgetter(data)
    if data_attr.__contains__("animations") then
        return
    end
    local output = python.builtins.dict()
    output["defined_in"] = data["defined_in"]
    output["animations"] = data
    python.as_attrgetter(output["animations"]).__delitem__("defined_in")
    return output
end