import Comparison.ComparerImporter.ComparerIntermediate as ComparerIntermediate
import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.GroupIntermediate as GroupIntermediate
import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerImporter.IntermediateCapabilities as IntermediateCapabilities
import Comparison.ComparerImporter.ListComparerIntermediate as ListComparerIntermediate
import Comparison.ComparerImporter.NormalizerFunctionIntermediate as NormalizerFunctionIntermediate
import Comparison.ComparerImporter.TypeAliasIntermediate as TypeAliasIntermediate
import Comparison.ListComparerSection as ListComparerSection
import Comparison.NbtModifier as NbtModifier
import Utilities.Nbt.NbtTypes as NbtTypes
import Utilities.TypeVerifier as TypeVerifier

def get_type_verifier(class_name:str) -> TypeVerifier.TypeVerifier:
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

    type_verifier = get_type_verifier(class_name)

    def __init__(self, data:ComparerTyping.NbtTagListTypedDict, name:str, index:int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index}, ["%s \"%s\"" % (self.class_name, name)])

        self.name = name
        self.comparer_str = data["comparer"]
        self.endianness = data.get("endianness", None)
        self.field = data.get("field", "item")
        self.measure_length = data.get("measure_length", False)
        self.normalizer_strs = None if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"])
        self.ordered = data.get("ordered", True)
        self.print_all = data.get("print_all", False)
        self.print_flat = data.get("print_flat", False)
        self.types_strs = data["types"]

        self.comparer:ComparerIntermediate.ComparerIntermediate|GroupIntermediate.GroupIntermediate|None = None
        self.types:list[type|TypeAliasIntermediate.TypeAliasIntermediate]|None = None
        self.links_to_other_intermediates:list[Intermediate.Intermediate] = []
        self.parents:list[Intermediate.Intermediate] = []
        self.normalizers:list[NormalizerFunctionIntermediate.NormalizerFunctionIntermediate]|None = None
        self.types_final:list[type] = []
        self.final:ListComparerSection.ListComparerSection|None = None

        self.children_has_normalizer = False

    def create_final_get_modifier(self) -> NbtModifier.NbtModifier|None:
        default_endianness = NbtModifier.get_endianness(self.endianness)
        return NbtModifier.NbtModifier(default_endianness)

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
    type_verifier = get_type_verifier(class_name)

class NbtTagIntArrayComparerIntermediate(NbtTagListComparerIntermediate):

    class_name_article = "an NbtTagIntArray"
    class_name = "NbtTagIntArray"
    my_type = [NbtTypes.TAG_Int_Array]
    required_types = [NbtTypes.TAG_Int]
    type_verifier = get_type_verifier(class_name)

class NbtTagLongArrayComparerIntermediate(NbtTagListComparerIntermediate):

    class_name_article = "an NbtTagLongArray"
    class_name = "NbtTagLongArray"
    my_type = [NbtTypes.TAG_Long_Array]
    required_types = [NbtTypes.TAG_Long]
    type_verifier = get_type_verifier(class_name)
