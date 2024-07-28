return function (data)
    if python.builtins.type(data) == python.builtins.dict then
        local output = python.builtins.list()
        local output_attr = python.as_attrgetter(output)
        output_attr.append(data)
        return output
    end
end