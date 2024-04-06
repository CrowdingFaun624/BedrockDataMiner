from typing import Any, Callable, Literal

import Comparison.ComparerImporter.ComparerIntermediate as ComparerIntermediate
import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.GroupIntermediate as GroupIntermediate
import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerImporter.TypedDictComparerIntermediate as TypedDictComparerIntermediate
import Comparison.ComparerImporter.IntermediateCapabilities as IntermediateCapabilities
import Comparison.ComparerImporter.NormalizerFunctionIntermediate as NormalizerFunctionIntermediate
import Comparison.ComparerSection as ComparerSection
import Comparison.NbtModifier as NbtModifier
import Comparison.TypedDictComparerSection as TypedDictComparerSection
import Utilities.Nbt.NbtTypes as NbtTypes
import Utilities.TypeVerifier as TypeVerifier

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

    def __init__(self, data:ComparerTyping.NbtTypedTagCompoundComparerTypedDict, name:str, index:int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index}, ["%s \"%s\"" % (self.class_name, name)])

        self.name = name
        self.field = data.get("field", "field")
        self.types_strs = data["types"]
        self.endianness = data.get("endianness", None)
        self.types:dict[str,ComparerTyping.NbtTypedTagCompoundTypeFilledTypedDict]|None = None
        self.imports = [] if "imports" not in data else ([data["imports"]] if isinstance(data["imports"], str) else data["imports"])
        self.measure_length = data.get("measure_length", False)
        self.normalizer_strs:list[str]|None = None if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"])
        self.print_all = data.get("print_all", False)
        self.tags = {key: (value["tags"] if "tags" in value else []) for key, value in self.types_strs.items()}

        self.links_to_other_intermediates:list[Intermediate.Intermediate] = []
        self.parents:list[Intermediate.Intermediate] = []
        self.normalizers:list[NormalizerFunctionIntermediate.NormalizerFunctionIntermediate]|None = None
        self.types_final:dict[tuple[str,type],ComparerSection.ComparerSection|None] = {}
        self.check_types_final:dict[str,tuple[list[type],ComparerIntermediate.ComparerIntermediate|GroupIntermediate.GroupIntermediate|None]] = {}
        self.final:TypedDictComparerSection.TypedDictComparerSection|None = None

        self.children_has_normalizer = self.children_has_normalizer_default


    def set_type(self, key:str, data:ComparerTyping.NbtTypedTagCompoundTypeTypedDict, intermediate_comparers:dict[str,Intermediate.Intermediate]) -> ComparerTyping.NbtTypedTagCompoundTypeFilledTypedDict:
        return {
            "comparer": self.set_comparer(key, data, intermediate_comparers),
            "endianness": None if "endianness" not in data else NbtModifier.get_endianness(data["endianness"]),
            "type": self.choose_types(key, data, intermediate_comparers),
        }

    def create_final_get_modifier(self) -> NbtModifier.NbtModifier:
        default_endianness = NbtModifier.get_endianness(self.endianness)
        assert self.types is not None
        keys_endianness = {key: (value["endianness"] if value["endianness"] is not None else default_endianness) for key, value in self.types.items()}
        return NbtModifier.NbtModifier(default_endianness, keys_endianness=keys_endianness)
