from typing import Callable

import Comparison.ComparerImporter.ComparerIntermediate as ComparerIntermediate
import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.DictComparerIntermediate as DictComparerIntermediate
import Comparison.ComparerImporter.GroupIntermediate as GroupIntermediate
import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerImporter.IntermediateCapabilities as IntermediateCapabilities
import Comparison.ComparerImporter.NormalizerFunctionIntermediate as NormalizerFunctionIntermediate
import Comparison.ComparerImporter.TypeAliasIntermediate as TypeAliasIntermediate
import Comparison.DictComparerSection as DictComparerSection
import Comparison.NbtModifier as NbtModifier
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
            TypeVerifier.TypedDictKeyTypeVerifier("endianness", "a str or None", False, TypeVerifier.EnumTypeVerifier(("big", "little", None))),
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

    def __init__(self, data:ComparerTyping.NbtTagCompoundTypedDict, name: str, index: int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index}, ["%s \"%s\"" % (self.class_name, name)])

        self.name = name
        self.comparer_str = data["comparer"]
        self.comparison_move_function_str = data.get("comparison_move_function", None)
        self.detect_key_moves = data.get("detect_key_moves", False)
        self.endianness = data.get("endianness", None)
        self.field = data.get("field", "field")
        self.measure_length = data.get("measure_length", False)
        self.normalizer_strs = None if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"])
        self.print_all = data.get("print_all", False)
        self.types_strs = data["types"]

        self.comparer:ComparerIntermediate.ComparerIntermediate|GroupIntermediate.GroupIntermediate|None = None
        self.comparison_move_function:Callable|None = None
        self.normalizers:list[NormalizerFunctionIntermediate.NormalizerFunctionIntermediate]|None = None
        self.types:list[type|TypeAliasIntermediate.TypeAliasIntermediate] = []
        self.links_to_other_intermediates:list[Intermediate.Intermediate] = []
        self.parents:list[Intermediate.Intermediate] = []
        self.types_final:tuple[type,...]|None = None
        self.final:DictComparerSection.DictComparerSection|None = None

        self.children_has_normalizer = False
    
    def create_final_get_modifier(self) -> NbtModifier.NbtModifier|None:
        default_endianness = NbtModifier.get_endianness(self.endianness)
        return NbtModifier.NbtModifier(default_endianness)
