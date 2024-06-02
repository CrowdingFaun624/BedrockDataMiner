--- @alias readFileMode `b` | `t`

--- @class (exact) zip_accessor
--- @field file_prepension string
--- @field name string
--- @field manager table
--- @field version { tags: string[] }
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

function zip_accessor:initialize()
    local has_ipa = false
    local has_double_assets = false
    for tag in python.iter( self.version.tags ) do
        if tag.__eq__( "ipa" ) then
            has_ipa = true
        elseif tag.__eq__( "double_assets" ) then
            has_double_assets = true
        end
    end
    if has_ipa then
        self.file_prepension = "Payload/minecraftpe.app/data/"
    elseif has_double_assets then
        self.file_prepension = "assets/assets/"
    else
        self.file_prepension = "assets/"
    end
end

function zip_accessor:modify_file_name( file_name )
    if file_name == nil then
        return self.file_prepension
    end
    return self.file_prepension .. file_name
end

function zip_accessor:trim_file_name( file_name )
    local file_prepension_length = self.file_prepension:len()
    return file_name:sub( file_prepension_length + 1 ) -- lua is 1-indexed
end

return zip_accessor
