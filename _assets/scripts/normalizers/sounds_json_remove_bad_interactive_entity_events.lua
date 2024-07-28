return function (data)
    local data_attr = python.as_attrgetter(data)
    local events_to_delete = {}
    for index, key_value in python.enumerate(data_attr.items()) do
        local event_name = key_value[0]
        local event_properties = key_value[1]
        if type(event_properties) ~= "string" then
            if not python.as_attrgetter(event_properties).__contains__("default") then
                table.insert(events_to_delete, event_name)
            end
        end
    end
    for index, event_to_delete in pairs(events_to_delete) do
        data_attr.__delitem__(event_to_delete)
    end
end