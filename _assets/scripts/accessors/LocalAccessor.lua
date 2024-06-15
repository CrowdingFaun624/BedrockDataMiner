local local_accessor = {}

local_accessor.inherit = "SubDirectoryAccessor"

function local_accessor:get_directory_base(file_type_arguments, os, pathlib2)
    local has_ipa = false
    local has_double_assets = false
    for tag in python.iter( self.version.tags ) do
        if tag.__eq__( "ipa" ) then
            has_ipa = true
        elseif tag.__eq__( "double_assets" ) then
            has_double_assets = true
        end
    end
    local file_prepension
    if has_ipa then
        file_prepension = "Payload/minecraftpe.app/data/"
    elseif has_double_assets then
        file_prepension = "assets/assets/"
    else
        file_prepension = "assets/"
    end
    return "C:\\Program Files\\WindowsApps" .. file_type_arguments.file_path .. file_prepension
end

return local_accessor
