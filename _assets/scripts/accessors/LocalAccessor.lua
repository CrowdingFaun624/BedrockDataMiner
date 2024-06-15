local local_accessor = {}

local_accessor.inherit = "SubDirectoryAccessor"

function local_accessor:get_directory_base(file_type_arguments, os, pathlib2)
    local file_prepension
    if self.version.has_tag("ipa") then
        file_prepension = "Payload/minecraftpe.app/data/"
    elseif self.version.has_tag("double_assets") then
        file_prepension = "assets/assets/"
    else
        file_prepension = "assets/"
    end
    return "C:\\Program Files\\WindowsApps" .. file_type_arguments.file_path .. file_prepension
end

return local_accessor
