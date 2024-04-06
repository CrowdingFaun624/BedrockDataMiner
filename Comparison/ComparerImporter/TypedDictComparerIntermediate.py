from typing import Any, Callable, cast, Generator, Iterable, Sequence

import Comparison.ComparerImporter.ComparerIntermediate as ComparerIntermediate
import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerImporter.IntermediateCapabilities as IntermediateCapabilities
import Comparison.ComparerImporter.GroupIntermediate as GroupIntermediate
import Comparison.ComparerImporter.NormalizerFunctionIntermediate as NormalizerFunctionIntermediate
import Comparison.ComparerImporter.TypeAliasIntermediate as TypeAliasIntermediate
import Comparison.ComparerSection as ComparerSection
import Comparison.Modifier as Modifier
import Comparison.Normalizer as Normalizer
import Comparison.TypedDictComparerSection as TypedDictComparerSection
import Utilities.TypeVerifier as TypeVerifier

COMPARER_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"is_comparer": True}, {"is_group": True}])
IMPORTABLE_KEYS_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"has_importable_keys": True}])
NORMALIZER_FUNCTION_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"is_normalizer_function": True}])
TYPE_ALIAS_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"is_type_alias": True}])

class TypedDictComparerIntermediate(ComparerIntermediate.ComparerIntermediate):

    class_name_article = "a TypedDict"
    class_name = "TypedDict"

    my_type = [dict]

    my_properties = IntermediateCapabilities.Capabilities(has_importable_keys=True, is_comparer=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
            TypeVerifier.TypedDictKeyTypeVerifier("imports", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier("TypedDict")),
            TypeVerifier.TypedDictKeyTypeVerifier("types", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.TypedDictTypeVerifier(
                TypeVerifier.TypedDictKeyTypeVerifier("type", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
                TypeVerifier.TypedDictKeyTypeVerifier("comparer", "a str or None", False, (str, type(None))),
                TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
            ), "a dict", "a str", "a dict")),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("index", "an int", True, int),
    )

    def __init__(self, data:ComparerTyping.TypedDictComparerTypedDict, name:str, index:int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index}, ["%s \"%s\"" % (self.class_name, name)])

        self.name = name
        self.field = data.get("field", "field")
        self.types_strs = data["types"]
        self.types:dict[str,ComparerTyping.TypedDictTypeFilledTypedDict]|None = None
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

    def choose_types_type_iterator(self, data:ComparerTyping.TypedDictTypeTypedDict) -> Generator[tuple[int|None, str], None, None]:
        '''Yields the index of the type_str and the type_str, or None and the type_str if it is not a list'''
        if isinstance(data["type"], str):
            yield (None, data["type"])
        else:
            yield from enumerate(data["type"])

    def choose_types(self, key:str, data:ComparerTyping.TypedDictTypeTypedDict, intermediate_comparers:dict[str,Intermediate.Intermediate]) -> list[type|TypeAliasIntermediate.TypeAliasIntermediate]:
        types:list[type|TypeAliasIntermediate.TypeAliasIntermediate] = []
        already_keys:set[str] = set()
        for index, type_str in self.choose_types_type_iterator(data):
            if type_str in already_keys:
                raise KeyError("Duplicate type \"%s\" of key \"%s\" of %s \"%s\"." % (type_str, key, self.class_name, self.name))
            already_keys.add(type_str)

            if type_str in ComparerTyping.DEFAULT_TYPES:
                types.append(ComparerTyping.DEFAULT_TYPES[type_str])
            else:
                choose_comparer_keys:list[str|int] = ["types", key, "type"] if index is None else ["types", key, "type", index]
                type_intermediate:TypeAliasIntermediate.TypeAliasIntermediate = self.choose_intermediate(type_str, TYPE_ALIAS_REQUEST_PROPERTIES, intermediate_comparers, choose_comparer_keys)
                self.links_to_other_intermediates.append(type_intermediate)
                type_intermediate.parents.append(self)
                types.append(type_intermediate)
        return types

    def set_imports(self, intermediate_comparers:dict[str,Intermediate.Intermediate], imports:list[str]) -> list["TypedDictComparerIntermediate"]:
        return [self.choose_intermediate(imported_comparer_str, IMPORTABLE_KEYS_REQUEST_PROPERTIES, intermediate_comparers, ["imports", index]) for index, imported_comparer_str in enumerate(imports)]

    def add_import_to_self(self, imports:list["TypedDictComparerIntermediate"]) -> None:
        for comparer in imports:
            for new_key, new_value in comparer.types_strs.items():
                if new_key in self.types_strs: continue
                self.types_strs[new_key] = new_value

    def set_comparer(self, key:str, data:ComparerTyping.TypedDictTypeTypedDict, intermediate_comparers:dict[str,Intermediate.Intermediate]) -> ComparerIntermediate.ComparerIntermediate|GroupIntermediate.GroupIntermediate|None:
        if "comparer" not in data or data["comparer"] is None: return None
        comparer:ComparerIntermediate.ComparerIntermediate|GroupIntermediate.GroupIntermediate = self.choose_intermediate(data["comparer"], COMPARER_REQUEST_PROPERTIES, intermediate_comparers, ["types", key, "comparer"])
        self.links_to_other_intermediates.append(comparer)
        comparer.parents.append(self)
        return comparer

    def set_type(self, key:str, data:ComparerTyping.TypedDictTypeTypedDict, intermediate_comparers:dict[str,Intermediate.Intermediate]) -> ComparerTyping.TypedDictTypeFilledTypedDict:
        return {
            "comparer": self.set_comparer(key, data, intermediate_comparers),
            "type": self.choose_types(key, data, intermediate_comparers),
        }

    def set_types(self, intermediate_comparers:dict[str,Intermediate.Intermediate], types_strs:dict[str,ComparerTyping.TypedDictTypeTypedDict]) -> dict[str,ComparerTyping.TypedDictTypeFilledTypedDict]:
        return {key: self.set_type(key, data, intermediate_comparers) for key, data in types_strs.items()}

    def set_normalizers(self, intermediate_comparers:dict[str,Intermediate.Intermediate], normalizer_strs:list[str]|None) -> list[NormalizerFunctionIntermediate.NormalizerFunctionIntermediate]|None:
        if normalizer_strs is None:
            return None
        else:
            normalizers:list[NormalizerFunctionIntermediate.NormalizerFunctionIntermediate] = [self.choose_intermediate(normalizer_str, NORMALIZER_FUNCTION_REQUEST_PROPERTIES, intermediate_comparers, ["normalizer"]) for normalizer_str in normalizer_strs]
            return normalizers

    def set(self, intermediate_comparers:dict[str,Intermediate.Intermediate], functions:dict[str,Callable]) -> None:
        imports = self.set_imports(intermediate_comparers, self.imports)
        self.link_intermediates(imports)
        self.add_import_to_self(imports)

        self.types = self.set_types(intermediate_comparers, self.types_strs)
        self.normalizers = self.set_normalizers(intermediate_comparers, self.normalizer_strs)
        if self.normalizers is not None:
            self.link_intermediates(self.normalizers)

    def create_final_get_final_normalizers(self) -> list[Normalizer.Normalizer]|None:
        return None if self.normalizers is None else [cast(Normalizer.Normalizer, normalizer.final) for normalizer in self.normalizers]

    def create_final_get_modifier(self) -> Modifier.Modifier|None:
        return None

    def create_final_get_final(self, normalizer_final:list[Normalizer.Normalizer]|None, modifier:Modifier.Modifier|None) -> TypedDictComparerSection.TypedDictComparerSection:
        return TypedDictComparerSection.TypedDictComparerSection(
            name=self.field,
            types=self.types_final,
            measure_length=self.measure_length,
            normalizer=normalizer_final,
            print_all=self.print_all,
            children_has_normalizer=self.children_has_normalizer,
            modifier=modifier,
        )

    def create_final(self) -> None:
        normalizer_final = self.create_final_get_final_normalizers()
        modifier = self.create_final_get_modifier()
        self.final = self.create_final_get_final(normalizer_final, modifier)

    def expand_types(self, types:Iterable[type|TypeAliasIntermediate.TypeAliasIntermediate]) -> Generator[type,None,None]:
        for item in types:
            if isinstance(item, type): yield item
            else:
                assert item.types is not None
                yield from item.types

    def link_finals(self) -> None:
        assert self.types is not None
        for types_key, types_value in self.types.items():
            comparer = types_value["comparer"]
            if isinstance(comparer, GroupIntermediate.GroupIntermediate):
                assert comparer.final is not None
                for group_type, group_comparer_section in comparer.final.items():
                    self.types_final[types_key, group_type] = group_comparer_section
                self.check_types_final[types_key] = (list(self.expand_types(types_value["type"])), comparer)
            else:
                key_types = list(self.expand_types(types_value["type"]))
                comparer_final = (comparer.final if comparer is not None else None)
                for key_type in key_types:
                    self.types_final[types_key, key_type] = comparer_final
                self.check_types_final[types_key] = (list(self.expand_types(types_value["type"])), comparer)

    def check(self) -> list[Exception]|None:
        assert self.final is not None
        self.final.check_initialization_parameters()
        exceptions:list[Exception] = []
        for key, (key_types, comparer) in self.check_types_final.items():
            if comparer is None:
                for type_item in key_types:
                    if type_item in ComparerTyping.REQUIRES_COMPARER_TYPES:
                        exceptions.append(TypeError("Key \"%s\" of %s \"%s\" accepts type %s, but has a null comparer!" % (key, self.class_name, self.name, type_item.__name__)))
            else:
                if set(key_types) != set(comparer.my_type):
                    my_types = ", ".join(type_item.__name__ for type_item in sorted(key_types, key=lambda x: x.__name__))
                    its_types = ", ".join(type_item.__name__ for type_item in sorted(comparer.my_type, key=lambda x: x.__name__))
                    exceptions.append(TypeError("Key \"%s\" of %s \"%s\" accepts types [%s], but its comparer, \"%s\", only accepts type [%s]!" % (key, self.class_name, self.name, my_types, comparer.name, its_types)))
        return exceptions

    def finalize_finals(self) -> None:
        assert self.final is not None
        self.final.finalize()
