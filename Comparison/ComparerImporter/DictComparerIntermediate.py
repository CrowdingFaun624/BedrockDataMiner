from typing import Callable, cast

import Comparison.ComparerImporter.ComparerIntermediate as ComparerIntermediate
import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.GroupIntermediate as GroupIntermediate
import Comparison.ComparerImporter.NormalizerFunctionIntermediate as NormalizerFunctionIntermediate
import Comparison.ComparerImporter.TypeAliasIntermediate as TypeAliasIntermediate
import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerSection as ComparerSection
import Comparison.ComparerImporter.IntermediateCapabilities as IntermediateCapabilities
import Comparison.DictComparerSection as DictComparerSection
import Comparison.Modifier as Modifier
import Comparison.Normalizer as Normalizer
import Utilities.TypeVerifier as TypeVerifier

COMPARER_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"is_comparer": True}, {"is_group": True}])
NORMALIZER_FUNCTION_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"is_normalizer_function": True}])
TYPE_ALIAS_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"is_type_alias": True}])

class DictComparerIntermediate(ComparerIntermediate.ComparerIntermediate):

    class_name_article = "a Dict"
    class_name = "Dict"

    my_type = [dict]

    my_properties = IntermediateCapabilities.Capabilities(is_comparer=True)

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

    def __init__(self, data:ComparerTyping.DictComparerTypedDict, name:str, index:int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index})

        self.name = name
        self.comparer_str = data["comparer"]
        self.comparison_move_function_str = data.get("comparison_move_function", None)
        self.detect_key_moves = data.get("detect_key_moves", False)
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

    def choose_types(self, key:str, types_strs:list[str], intermediate_comparers:dict[str,Intermediate.Intermediate]) -> list[type|TypeAliasIntermediate.TypeAliasIntermediate]:
        types:list[type|TypeAliasIntermediate.TypeAliasIntermediate] = []
        already_types:set[str] = set()
        for type_str in types_strs:
            if type_str in already_types:
                raise KeyError("Duplicate type \"%s\" of key \"%s\" of %s \"%s\"." % (type_str, key, self.class_name, self.name))
            already_types.add(type_str)
            if type_str in ComparerTyping.DEFAULT_TYPES:
                types.append(ComparerTyping.DEFAULT_TYPES[type_str])
            else:
                type_alias = self.choose_intermediate(type_str, TYPE_ALIAS_REQUEST_PROPERTIES, intermediate_comparers, [key])
                self.links_to_other_intermediates.append(type_alias)
                types.append(type_alias)
        return types

    def set_comparer(self, intermediate_comparers:dict[str,Intermediate.Intermediate], comparer_str:str|None) -> ComparerIntermediate.ComparerIntermediate|GroupIntermediate.GroupIntermediate|None:
        if self.comparer_str is None:
            return None
        else:
            comparer:ComparerIntermediate.ComparerIntermediate|GroupIntermediate.GroupIntermediate = self.choose_intermediate(self.comparer_str, COMPARER_REQUEST_PROPERTIES, intermediate_comparers, ["comparer"])
            self.link_intermediates(comparer)
            return comparer

    def set_comparison_move_function(self, functions:dict[str,Callable], comparison_move_function_str:str|None) -> Callable|None:
        if comparison_move_function_str is None:
            return None
        else:
            if comparison_move_function_str not in functions:
                raise KeyError("Function \"%s\", referenced in key \"comparison_move_function\" of %s \"%s\", does not exist!" % (comparison_move_function_str, self.class_name, self.name))
            return functions[comparison_move_function_str]

    def set_normalizers(self, intermediate_comparers:dict[str,Intermediate.Intermediate], normalizer_strs:list[str]|None) -> list[NormalizerFunctionIntermediate.NormalizerFunctionIntermediate]|None:
        if normalizer_strs is None:
            return None
        else:
            normalizers:list[NormalizerFunctionIntermediate.NormalizerFunctionIntermediate] = [self.choose_intermediate(normalizer_str, NORMALIZER_FUNCTION_REQUEST_PROPERTIES, intermediate_comparers, ["normalizer"]) for normalizer_str in normalizer_strs]
            self.link_intermediates(normalizers)
            return normalizers

    def set(self, intermediate_comparers:dict[str,Intermediate.Intermediate], functions:dict[str,Callable]) -> None:
        self.comparer = self.set_comparer(intermediate_comparers, self.comparer_str)
        self.comparison_move_function = self.set_comparison_move_function(functions, self.comparison_move_function_str)
        self.types = self.choose_types("types", self.types_strs, intermediate_comparers)
        self.normalizers = self.set_normalizers(intermediate_comparers, self.normalizer_strs)

    def create_final_get_types_final(self, types:list[type|TypeAliasIntermediate.TypeAliasIntermediate]) -> tuple[type,...]:
        '''Expands a list of types and TypeAliases into just a tuple of types.'''
        output:list[type] = []
        for types_item in types:
            if isinstance(types_item, type):
                output.append(types_item)
            else:
                assert types_item.types is not None
                output.extend(types_item.types)
        return tuple(output)

    def create_final_get_normalizers(self, normalizers:list[NormalizerFunctionIntermediate.NormalizerFunctionIntermediate]|None) -> list[Normalizer.Normalizer]|None:
        return None if normalizers is None else [cast(Normalizer.Normalizer, normalizer.final) for normalizer in normalizers]

    def create_final_get_modifier(self) -> Modifier.Modifier|None:
        return None

    def create_final_get_final(self, normalizer_final:list[Normalizer.Normalizer]|None, modifier:Modifier.Modifier|None) -> DictComparerSection.DictComparerSection:
        return DictComparerSection.DictComparerSection(
            name=self.field,
            comparer=None,
            types=self.types_final,
            detect_key_moves=self.detect_key_moves,
            comparison_move_function=self.comparison_move_function,
            measure_length=self.measure_length,
            normalizer=normalizer_final,
            print_all=self.print_all,
            children_has_normalizer=self.children_has_normalizer,
            modifier=modifier,
        )

    def create_final(self) -> None:
        self.types_final = self.create_final_get_types_final(self.types)
        normalizer_final = self.create_final_get_normalizers(self.normalizers)
        modifier = self.create_final_get_modifier()
        self.final = self.create_final_get_final(normalizer_final, modifier)

    def link_finals(self) -> None:
        assert self.final is not None
        if self.comparer is None:
            self.final.comparer = None
        else:
            assert self.comparer.final is not None
            self.final.comparer = cast(ComparerSection.ComparerSection|None|dict[type,ComparerSection.ComparerSection|None], self.comparer.final)

    def check(self) -> list[Exception]|None:
        assert self.final is not None
        assert self.types_final is not None
        self.final.check_initialization_parameters()
        if self.comparer is None:
            for value_type in self.types_final:
                if value_type in ComparerTyping.REQUIRES_COMPARER_TYPES:
                    return [TypeError("%s \"%s\" accepts type %s, but has a null comparer!" % (self.class_name, self.name, value_type.__name__))]
        else:
            for value_type in self.types_final:
                if value_type not in self.comparer.my_type:
                    its_types = ", ".join(type_item.__name__ for type_item in self.comparer.my_type)
                    return [TypeError("%s \"%s\" accepts type %s, but its comparer, \"%s\", only accepts type [%s]!" % (self.class_name, self.name, value_type.__name__, self.comparer.name, its_types))]
