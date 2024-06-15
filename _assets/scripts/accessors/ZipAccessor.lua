--- @alias readFileMode `b` | `t`

--- @class (exact) zip_accessor
--- @field inherit string
--- @field file_prepension string
--- @field name string
--- @field manager table
--- @field version { has_tag: fun( tag: string): (boolean) }
--- @field initialize fun( self ): ( nil )
--- @field modify_file_name fun( self, file_name: string ): ( string )
--- @field trim_file_name fun( self, file_name: string): ( string )
--- @field install_all fun( self ): ( nil )
--- @field file_exists fun( self, file_name: string ): ( boolean )
--- @field get_files_in fun( self, parent: string ): ( string[] )
--- @field get_file_list fun( self ): ( string[] )
--- @field get_full_file_list fun( self ): ( string[] )
--- @field read fun( self, file_name: string, mode: readFileMode ): ( string )
--- @field get_file fun( self, file_name: string, mode: readFileMode ): ( table )
--- @field all_done fun( self ): (nil)
local zip_accessor = {}

zip_accessor.inherit = "SubDirectoryAccessor"

function zip_accessor:initialize()
    if self.version.has_tag("ipa") then
        self.file_prepension = "Payload/minecraftpe.app/data/"
    elseif self.version.has_tag("double_assets") then
        self.file_prepension = "assets/assets/"
    else
        self.file_prepension = "assets/"
    end
end

return zip_accessor
