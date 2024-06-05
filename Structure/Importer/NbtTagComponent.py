import Structure.Importer.Capabilities as Capabilities
import Structure.Importer.DictComponent as DictComponent
import Structure.Importer.ImporterConfig as ImporterConfig
import Structure.Importer.KeymapComponent as KeymapComponent
import Structure.Importer.ListComponent as ListComponent
import Utilities.Exceptions as Exceptions
import Utilities.Nbt.NbtTypes as NbtTypes


class NbtTagCompoundComponent(DictComponent.DictComponent):

    class_name_article = "an NbtTagCompound"
    class_name = "NbtTagCompound"
    my_type = [NbtTypes.TAG_Compound]
    my_capabilities = Capabilities.Capabilities(has_keys=True, is_nbt_tag=True, is_structure=True)

class NbtTagListComponent(ListComponent.ListComponent):

    class_name_article = "an NbtTagList"
    class_name = "NbtTagList"
    my_type = [NbtTypes.TAG_List]
    required_types:list[type]|None = None
    my_capabilities = Capabilities.Capabilities(is_nbt_tag=True, is_structure=True)

    def check_required_type(self) -> list[Exception]:
        if self.required_types is None: return []
        for type in self.types_field.get_types():
            if type not in self.required_types:
                output:Exception = Exceptions.InvalidComponentTypeError(self, tuple(self.required_types), type)
                return [output]
        return []

    def check(self, config:ImporterConfig.ImporterConfig) -> list[Exception]:
        exceptions = super().check(config)
        exceptions.extend(self.check_required_type())
        return exceptions

class NbtTagByteArrayComponent(NbtTagListComponent):

    class_name_article = "an NbtTagByteArray"
    class_name = "NbtTagByteArray"
    my_type = [NbtTypes.TAG_Byte_Array]
    required_types = [NbtTypes.TAG_Byte]

class NbtTagIntArrayComponent(NbtTagListComponent):

    class_name_article = "an NbtTagIntArray"
    class_name = "NbtTagIntArray"
    my_type = [NbtTypes.TAG_Int_Array]
    required_types = [NbtTypes.TAG_Int]

class NbtTagLongArrayComponent(NbtTagListComponent):

    class_name_article = "an NbtTagLongArray"
    class_name = "NbtTagLongArray"
    my_type = [NbtTypes.TAG_Long_Array]
    required_types = [NbtTypes.TAG_Long]

class NbtKeymapTagCompoundComponent(KeymapComponent.KeymapComponent):

    class_name_article = "an NbtKeymapTagCompound"
    class_name = "NbtKeymapTagCompound"
    my_type = [NbtTypes.TAG_Compound]
    my_capabilities = Capabilities.Capabilities(has_importable_keys=True, has_keys=True, is_nbt_tag=True, is_structure=True)
    children_has_normalizer_default = True
