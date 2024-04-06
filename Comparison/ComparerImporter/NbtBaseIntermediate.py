from typing import Callable, cast

import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.ComparerIntermediate as ComparerIntermediate
import Comparison.ComparerImporter.GroupIntermediate as GroupIntermediate
import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerImporter.IntermediateCapabilities as IntermediateCapabilities
import Comparison.ComparerImporter.NormalizerFunctionIntermediate as NormalizerFunctionIntermediate
import Comparison.ComparerImporter.TypeAliasIntermediate as TypeAliasIntermediate
import Comparison.NbtBaseComparerSection as NbtBaseComparerSection
import Comparison.Normalizer as Normalizer
import Utilities.Nbt.Endianness as Endianness
import Utilities.Nbt.NbtTypes as NbtTypes
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.TypeVerifier as TypeVerifier

COMPARER_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"is_comparer": True, "is_nbt_tag": True}, {"is_group": True}])
NORMALIZER_FUNCTION_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"is_normalizer_function": True}])
TYPE_ALIAS_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"is_type_alias": True}])

class NbtBaseIntermediate(ComparerIntermediate.ComparerIntermediate):

    class_name_article = "an NbtBase"
    class_name = "NbtBase"

    my_properties = IntermediateCapabilities.Capabilities(is_comparer=True, is_nbt_base=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("comparer", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("endianness", "a str", True, TypeVerifier.EnumTypeVerifier(("big", "little"))),
            TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
            TypeVerifier.TypedDictKeyTypeVerifier("types", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("index", "an int", True, int),
    )

    def __init__(self, data:ComparerTyping.NbtBaseTypedDict, name: str, index: int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index}, ["%s \"%s\"" % (self.class_name, name)])

        self.name = name
        self.comparer_str = data["comparer"]
        self.endianness = data["endianness"]
        self.types_strs = data["types"]
        self.normalizer_strs = None if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"])

        self.links_to_other_intermediates:list[Intermediate.Intermediate] = []
        self.parents:list[Intermediate.Intermediate] = []
        self.children_has_normalizer = True # All NbtBases have built-in normalizers that unpack the NBT
        self.types:list[type|TypeAliasIntermediate.TypeAliasIntermediate]|None = None
        self.types_final:list[type] = []
        self.final:NbtBaseComparerSection.NbtBaseComparerSection|None = None
        self.comparer:ComparerIntermediate.ComparerIntermediate|GroupIntermediate.GroupIntermediate|None = None

    def set(self, intermediate_comparers: dict[str, Intermediate.Intermediate], functions: dict[str, Callable]) -> None:
        self.comparer:ComparerIntermediate.ComparerIntermediate|GroupIntermediate.GroupIntermediate|None = self.choose_intermediate(self.comparer_str, COMPARER_REQUEST_PROPERTIES, intermediate_comparers, ["comparer"])
        assert self.comparer is not None
        self.links_to_other_intermediates.append(self.comparer)
        self.comparer.parents.append(self)

        self.types = []
        for index, type_str in enumerate(self.types_strs):
            if type_str in ComparerTyping.DEFAULT_TYPES:
                self.types.append(ComparerTyping.DEFAULT_TYPES[type_str])
            else:
                type_intermediate:TypeAliasIntermediate.TypeAliasIntermediate = self.choose_intermediate(type_str, TYPE_ALIAS_REQUEST_PROPERTIES, intermediate_comparers, ["types", index])
                self.links_to_other_intermediates.append(type_intermediate)
                type_intermediate.parents.append(self)
                self.types.append(type_intermediate)
        if self.normalizer_strs is None:
            self.normalizers = None
        else:
            self.normalizers:list[NormalizerFunctionIntermediate.NormalizerFunctionIntermediate]|None = [self.choose_intermediate(normalizer_str, NORMALIZER_FUNCTION_REQUEST_PROPERTIES, intermediate_comparers, ["normalizer"]) for normalizer_str in self.normalizer_strs]
            self.links_to_other_intermediates.extend(self.normalizers)
            for normalizer in self.normalizers:
                normalizer.parents.append(self)

    def create_final_get_types_final(self, types:list[type|TypeAliasIntermediate.TypeAliasIntermediate]|None) -> list[type]:
        types_final:list[type] = []
        assert types is not None
        for types_item in types:
            if isinstance(types_item, type):
                types_final.append(types_item)
            else:
                assert types_item.types is not None
                types_final.extend(types_item.types)
        return types_final

    def create_final_get_normalizers(self, normalizers:list[NormalizerFunctionIntermediate.NormalizerFunctionIntermediate]|None) -> list[Normalizer.Normalizer]|None:
        return None if self.normalizers is None else [cast(Normalizer.Normalizer, normalizer.final) for normalizer in self.normalizers]

    def get_endianness(self, endianness:str) -> Endianness.End:
        match endianness:
            case "big": return Endianness.End.BIG
            case "little": return Endianness.End.LITTLE
            case _: raise ValueError("Invalid endianness \"%s\"!" % endianness)

    def create_final_get_final(self, normalizers_final:list[Normalizer.Normalizer]|None) -> NbtBaseComparerSection.NbtBaseComparerSection:
        return NbtBaseComparerSection.NbtBaseComparerSection(
            name = self.name,
            comparer = None,
            endianness=self.get_endianness(self.endianness),
            types = tuple(self.types_final),
            normalizer = normalizers_final,
            children_has_normalizers=self.children_has_normalizer,
        )

    def create_final(self) -> None:
        self.types_final = self.create_final_get_types_final(self.types)
        self.my_type = self.types_final
        normalizers_final = self.create_final_get_normalizers(self.normalizers)
        self.final = self.create_final_get_final(normalizers_final)
    
    def link_finals(self) -> None:
        assert self.final is not None
        assert self.comparer is not None
        assert self.comparer.final is not None
        self.final.comparer = self.comparer.final
    
    def check(self) -> list[Exception] | None:
        assert self.final is not None
        assert self.comparer is not None
        self.final.check_initialization_parameters()
        for value_type in self.types_final:
            if not issubclass(value_type, NbtTypes.TAG):
                return [TypeError("%s \"%s\" cannot except non-NbtTag type %s!" % (self.class_name, self.name, value_type.__name__))]
            if value_type not in self.comparer.my_type:
                its_types = ", ".join(type_item.__name__ for type_item in self.comparer.my_type)
                return [TypeError("%s \"%s\" accepts type %s, but its comparer, \"%s\", only accepts type [%s]!" % (self.class_name, self.name, value_type.__name__, self.comparer.name, its_types))]
