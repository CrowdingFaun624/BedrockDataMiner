import Comparison.ComparerImporter.DictComparerIntermediate as DictComparerIntermediate
import Comparison.ComparerImporter.ListComparerIntermediate as ListComparerIntermediate
import Comparison.ComparerImporter.TypedDictComparerIntermediate as TypedDictComparerIntermediate
import Comparison.ComparerImporter.IntermediateCapabilities as IntermediateCapabilities
import Utilities.Nbt.NbtTypes as NbtTypes
import Utilities.TypeVerifier as TypeVerifier

class NbtTagCompoundComparerIntermediate(DictComparerIntermediate.DictComparerIntermediate):

    class_name_article = "an NbtTagCompound"
    class_name = "NbtTagCompound"

    my_type = [NbtTypes.TAG_Compound]

    my_properties = IntermediateCapabilities.Capabilities(is_comparer=True, is_nbt_tag=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("comparer", "a str or None", True, (str, type(None))),
            TypeVerifier.TypedDictKeyTypeVerifier("comparison_move_function", "a str", False, str),
            TypeVerifier.TypedDictKeyTypeVerifier("detect_key_moves", "a bool", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
            TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
            TypeVerifier.TypedDictKeyTypeVerifier("types", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("index", "an int", True, int),
    )

def get_list_type_verifier(class_name:str) -> TypeVerifier.TypeVerifier:
    return TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("comparer", "a str or None", True, (str, type(None))),
            TypeVerifier.TypedDictKeyTypeVerifier("endianness", "a str or None", False, TypeVerifier.EnumTypeVerifier(("big", "little", None))),
            TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
            TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("ordered", "a bool", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("print_flat", "a bool", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
            TypeVerifier.TypedDictKeyTypeVerifier("types", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("index", "an int", True, int)
    )

class NbtTagListComparerIntermediate(ListComparerIntermediate.ListComparerIntermediate):

    class_name_article = "an NbtTagList"
    class_name = "NbtTagList"

    my_type = [NbtTypes.TAG_List]
    required_types:list[type]|None = None

    my_properties = IntermediateCapabilities.Capabilities(is_comparer=True, is_nbt_tag=True)

    type_verifier = get_list_type_verifier(class_name)

    def check_required_type(self) -> list[Exception]:
        assert self.types is not None
        if self.required_types is None: return []
        for type in self.types:
            if type not in self.required_types:
                return [TypeError("%s \"%s\" accepts type %s instead of only [%s]!" % (self.class_name, self.name, type, ", ".join(required_type.__name__ for required_type in self.required_types)))]
        return []

    def check(self) -> list[Exception]|None:
        assert self.final is not None
        exceptions:list[Exception] = []
        self.final.check_initialization_parameters()
        exceptions.extend(self.check_comparers())
        exceptions.extend(self.check_required_type())

class NbtTagByteArrayComparerIntermediate(NbtTagListComparerIntermediate):

    class_name_article = "an NbtTagByteArray"
    class_name = "NbtTagByteArray"
    my_type = [NbtTypes.TAG_Byte_Array]
    required_types = [NbtTypes.TAG_Byte]
    type_verifier = get_list_type_verifier(class_name)

class NbtTagIntArrayComparerIntermediate(NbtTagListComparerIntermediate):

    class_name_article = "an NbtTagIntArray"
    class_name = "NbtTagIntArray"
    my_type = [NbtTypes.TAG_Int_Array]
    required_types = [NbtTypes.TAG_Int]
    type_verifier = get_list_type_verifier(class_name)

class NbtTagLongArrayComparerIntermediate(NbtTagListComparerIntermediate):

    class_name_article = "an NbtTagLongArray"
    class_name = "NbtTagLongArray"
    my_type = [NbtTypes.TAG_Long_Array]
    required_types = [NbtTypes.TAG_Long]
    type_verifier = get_list_type_verifier(class_name)

class NbtTypedTagCompoundComparerIntermediate(TypedDictComparerIntermediate.TypedDictComparerIntermediate):

    class_name_article = "an NbtTypedTagCompound"
    class_name = "NbtTypedTagCompound"

    my_type = [NbtTypes.TAG_Compound]

    my_properties = IntermediateCapabilities.Capabilities(has_importable_keys=True, is_comparer=True, is_nbt_tag=True)
    children_has_normalizer_default = True

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("endianness", "a str", False, TypeVerifier.EnumTypeVerifier(("big", "little", None))),
            TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
            TypeVerifier.TypedDictKeyTypeVerifier("imports", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
            TypeVerifier.TypedDictKeyTypeVerifier("types", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.TypedDictTypeVerifier(
                TypeVerifier.TypedDictKeyTypeVerifier("type", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
                TypeVerifier.TypedDictKeyTypeVerifier("comparer", "a str or None", False, (str, type(None))),
                TypeVerifier.TypedDictKeyTypeVerifier("endianness", "a str", False, TypeVerifier.EnumTypeVerifier(("big", "little", None))),
                TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
            ), "a dict", "a str", "a dict")),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("index", "an int", True, int),
    )
