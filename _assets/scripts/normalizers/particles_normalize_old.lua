return function(data)
    local data_attr = python.as_attrgetter(data)
    if not data_attr.__contains__("particles") then
        return
    end
    local particle_identifier = nil
    for index, key in python.enumerate(data["particles"]) do
        particle_identifier = key
    end
    assert(particle_identifier ~= nil, "dictionary is empty; cannot find particle identifier")
    local output = python.builtins.dict()
    output["format_version"] = data["format_version"]
    output["defined_in"] = data["defined_in"]
    output["particle_effect"] = data["particles"][particle_identifier]
    output["particle_effect"]["description"] = python.builtins.dict()
    output["particle_effect"]["description"]["basic_render_parameters"] = data["particles"][particle_identifier]["basic_render_parameters"]
    output["particle_effect"]["description"]["identifier"] = particle_identifier
    python.as_attrgetter(output["particle_effect"]).__delitem__("basic_render_parameters")
    return output
end