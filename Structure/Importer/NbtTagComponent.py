import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.DictComponent as DictComponent
import Structure.Importer.ImporterConfig as ImporterConfig
import Structure.Importer.KeymapComponent as KeymapComponent
import Structure.Importer.ListComponent as ListComponent
import Utilities.Nbt.NbtTypes as NbtTypes


class NbtTagCompoundComponent(DictComponent.DictComponent):

    class_name_article = "an NbtTagCompound"
    class_name = "NbtTagCompound"
    my_type = [NbtTypes.TAG_Compound]
    my_properties = ComponentCapabilities.Capabilities(has_keys=True, is_nbt_tag=True, is_structure=True)

class NbtTagListComponent(ListComponent.ListComponent):

    class_name_article = "an NbtTagList"
    class_name = "NbtTagList"
    my_type = [NbtTypes.TAG_List]
    required_types:list[type]|None = None
    my_properties = ComponentCapabilities.Capabilities(is_nbt_tag=True, is_structure=True)

    def check_required_type(self) -> list[Exception]:
        if self.required_types is None: return []
        for type in self.types_field.get_types():
            if type not in self.required_types:
                return [TypeError("%s \"%s\" accepts type %s instead of only [%s]!" % (self.class_name, self.name, type, ", ".join(required_type.__name__ for required_type in self.required_types)))]
        return []

    def check(self, config:ImporterConfig.ImporterConfig) -> list[Exception]:
        super().check(config)
        assert self.final is not None
        exceptions:list[Exception] = []
        self.final.check_initialization_parameters()
        exceptions.extend(self.check_components())
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
    my_properties = ComponentCapabilities.Capabilities(has_importable_keys=True, has_keys=True, is_nbt_tag=True, is_structure=True)
    children_has_normalizer_default = True
