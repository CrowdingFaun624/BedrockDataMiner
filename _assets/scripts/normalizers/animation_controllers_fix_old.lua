return function (data)
    local data_attr = python.as_attrgetter(data)
    if data_attr.__contains__("animation_controllers") then
        return
    end
    local output = python.builtins.dict()
    output["defined_in"] = data["defined_in"]
    output["animation_controllers"] = data
    python.as_attrgetter(output["animation_controllers"]).__delitem__("defined_in")
    return output
end