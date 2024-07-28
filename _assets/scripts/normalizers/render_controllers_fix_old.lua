return function (data)
    local data_attr = python.as_attrgetter(data)
    if data_attr.__contains__("render_controllers") then
        return
    end
    local output = python.builtins.dict()
    output["defined_in"] = data["defined_in"]
    output["render_controllers"] = data
    data_attr.__delitem__("defined_in")
    return output
end