return function (data)
    if type(data) == "string" then
        local output = python.builtins.dict()
        output["name"] = data
        return output
    end
end