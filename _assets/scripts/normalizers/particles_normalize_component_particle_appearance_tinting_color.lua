return function (data)
    local py_type = python.builtins.type(data)
    if py_type == python.builtins.str or py_type == python.builtins.list then
        local result = python.as_attrgetter(python.builtins.list())
        result.append(data)
        return result
    end
end
