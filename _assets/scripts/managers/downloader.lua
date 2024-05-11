---@param io table
---@return nil
local install = function(io)
    return nil
end

return function ()
    return {
        install=install
    }
end