return function(data)
    local output = python.as_attrgetter(python.builtins.list())
    for index, behavior_pack in python.enumerate(data) do
        output.append(behavior_pack["name"])
    end
    return output
end