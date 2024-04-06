from typing import Callable, cast

import Comparison.ComparerImporter.ComparerIntermediate as ComparerIntermediate
import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerImporter.IntermediateCapabilities as IntermediateCapabilities
import Comparison.ComparerImporter.GroupIntermediate as GroupIntermediate
import Comparison.ComparerImporter.NormalizerFunctionIntermediate as NormalizerFunctionIntermediate
import Comparison.ComparerImporter.TypeAliasIntermediate as TypeAliasIntermediate
import Comparison.ListComparerSection as ListComparerSection
import Comparison.Normalizer as Normalizer
import Utilities.TypeVerifier as TypeVerifier

COMPARER_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"is_comparer": True}, {"is_group": True}])
NORMALIZER_FUNCTION_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"is_normalizer_function": True}])
TYPE_ALIAS_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"is_type_alias": True}])

class ListComparerIntermediate(ComparerIntermediate.ComparerIntermediate):

    class_name_article = "a List"
    class_name = "List"

    my_type = [list]

    my_properties = IntermediateCapabilities.Capabilities(is_comparer=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("comparer", "a str or None", True, (str, type(None))),
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

    def __init__(self, data:ComparerTyping.ListComparerTypedDict, name:str, index:int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index}, ["%s \"%s\"" % (self.class_name, name)])

        self.name = name
        self.comparer_str = data["comparer"]
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

    def set_comparer(self, intermediate_comparers:dict[str,Intermediate.Intermediate], comparer_str:str|None) -> ComparerIntermediate.ComparerIntermediate|GroupIntermediate.GroupIntermediate|None:
        if comparer_str is None:
            return None
        else:
            comparer = self.choose_intermediate(comparer_str, COMPARER_REQUEST_PROPERTIES, intermediate_comparers, ["comparer"])
            self.link_intermediates(comparer)
            return comparer
    
    def set_types(self, intermediate_comparers:dict[str,Intermediate.Intermediate], types_strs:list[str]) -> list[type|TypeAliasIntermediate.TypeAliasIntermediate]|None:
        types:list[type|TypeAliasIntermediate.TypeAliasIntermediate] = []
        for index, type_str in enumerate(types_strs):
            if type_str in ComparerTyping.DEFAULT_TYPES:
                types.append(ComparerTyping.DEFAULT_TYPES[type_str])
            else:
                type_intermediate:TypeAliasIntermediate.TypeAliasIntermediate = self.choose_intermediate(type_str, TYPE_ALIAS_REQUEST_PROPERTIES, intermediate_comparers, ["types", index])
                types.append(type_intermediate)
                self.link_intermediates(type_intermediate)
        return types
    
    def set_normalizers(self, intermediate_comparers:dict[str,Intermediate.Intermediate], normalizer_strs:list[str]|None) -> list[NormalizerFunctionIntermediate.NormalizerFunctionIntermediate]|None:
        if normalizer_strs is None:
            return None
        else:
            normalizers:list[NormalizerFunctionIntermediate.NormalizerFunctionIntermediate] = [self.choose_intermediate(normalizer_str, NORMALIZER_FUNCTION_REQUEST_PROPERTIES, intermediate_comparers, ["normalizer"]) for normalizer_str in normalizer_strs]
            self.link_intermediates(normalizers)
            return normalizers

    def set(self, intermediate_comparers:dict[str,Intermediate.Intermediate], functions:dict[str,Callable]) -> None:
        self.comparer = self.set_comparer(intermediate_comparers, self.comparer_str)
        self.types = self.set_types(intermediate_comparers, self.types_strs)
        self.normalizers = self.set_normalizers(intermediate_comparers, self.normalizer_strs)

    def create_final_get_final_types(self, types:list[type|TypeAliasIntermediate.TypeAliasIntermediate]|None) -> list[type]:
        types_final:list[type] = []
        assert types is not None
        for types_item in types:
            if isinstance(types_item, type):
                types_final.append(types_item)
            else:
                assert types_item.types is not None
                types_final.extend(types_item.types)
        return types_final

    def create_final_get_final_normalizers(self) -> list[Normalizer.Normalizer]|None:
        return None if self.normalizers is None else [cast(Normalizer.Normalizer, normalizer.final) for normalizer in self.normalizers]

    def create_final_get_final(self, normalizer_final:list[Normalizer.Normalizer]|None) -> ListComparerSection.ListComparerSection:
        return ListComparerSection.ListComparerSection(
            name=self.field,
            comparer=None,
            types=tuple(self.types_final),
            print_flat=self.print_flat,
            print_all=self.print_all,
            measure_length=self.measure_length,
            normalizer=normalizer_final,
            ordered=self.ordered,
            children_has_normalizer=self.children_has_normalizer,
        )

    def create_final(self) -> None:
        self.types_final:list[type] = self.create_final_get_final_types(self.types)
        normalizer_final = self.create_final_get_final_normalizers()
        self.final = self.create_final_get_final(normalizer_final, )

    def link_finals(self) -> None:
        assert self.final is not None
        if self.comparer is None:
            self.final.comparer = None
        else:
            self.final.comparer = self.comparer.final

    def check_comparers(self) -> list[Exception]:
        if self.comparer is None:
            for value_type in self.types_final:
                if value_type in ComparerTyping.REQUIRES_COMPARER_TYPES:
                    return [TypeError("%s \"%s\" accepts type %s, but has a null comparer!" % (self.class_name, self.name, value_type.__name__))]
        else:
            for value_type in self.types_final:
                if value_type not in self.comparer.my_type:
                    its_types = ", ".join(type_item.__name__ for type_item in self.comparer.my_type)
                    return [TypeError("%s \"%s\" accepts type %s, but its comparer, \"%s\", only accepts type [%s]!" % (self.class_name, self.name, value_type.__name__, self.comparer.name, its_types))]
        return []

    def check(self) -> list[Exception]|None:
        assert self.final is not None
        exceptions:list[Exception] = []
        self.final.check_initialization_parameters()
        exceptions.extend(self.check_comparers())
