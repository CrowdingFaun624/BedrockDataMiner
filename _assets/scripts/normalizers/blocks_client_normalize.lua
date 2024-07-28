return function (data)
    local output = python.builtins.dict()
    for index, block in python.enumerate(data) do
        output[block["name"]] = block["properties"]
    end
    return output
end