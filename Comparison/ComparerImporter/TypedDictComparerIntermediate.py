from typing import Callable, cast, Generator, Iterable

import Comparison.ComparerImporter.ComparerIntermediate as ComparerIntermediate
import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerImporter.GroupIntermediate as GroupIntermediate
import Comparison.ComparerImporter.NormalizerFunctionIntermediate as NormalizerFunctionIntermediate
import Comparison.ComparerImporter.TypeAliasIntermediate as TypeAliasIntermediate
import Comparison.ComparerSection as ComparerSection
import Comparison.Normalizer as Normalizer
import Comparison.TypedDictComparerSection as TypedDictComparerSection

class TypedDictComparerIntermediate(ComparerIntermediate.ComparerIntermediate):

    my_type = [dict]

    def __init__(self, data:ComparerTyping.TypedDictComparerTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("field", str, "a str", False),
            ("imports", (str, list), "a str or list", False),
            ("measure_length", bool, "a bool", False),
            ("normalizer", (str, list), "a str or list", False),
            ("print_all", bool, "a bool", False),
            ("type", str, "a str", True),
            ("types", dict, "a dict", True),
        ])
        if not all(isinstance(value, dict) for value in data["types"].values()):
            raise TypeError("A value of key \"types\" of TypedDict \"%s\" is not a dict!" % name)
        if "imports" in data and isinstance(data["imports"], list) and not all(isinstance(item, str) for item in data["imports"]):
            raise TypeError("An item of of key \"import\" of TypedDict \"%s\" is not a str!" % (name))
        for key, value in data["types"].items():
            if not isinstance(value, dict):
                raise TypeError("Item %s of key \"types\" of TypedDict \"%s\" is not a dict!" % (key, name))
            for value_key, value_value in value.items():
                match value_key:
                    case "type":
                        if not isinstance(value_value, (list, str)):
                            raise TypeError("Key \"%s\" of key \"%s\" of key \"types\" of TypedDict \"%s\" is not a list or str!" % (value_key, key, name))
                        if isinstance(value_value, list):
                            for type_index, type_item in enumerate(value_value):
                                if not isinstance(type_item, str):
                                    raise TypeError("Item %i of the key \"%s\" of key \"%s\" of key \"types\" of TypedDict \"%s\" is not a str!" % (type_index, value_key, key, name))
                    case "comparer":
                        if not (isinstance(value_value, str) or value_value is None):
                            raise TypeError("Key \"%s\" of key \"%s\" of key \"types\" of TypedDict \"%s\" is not a str or None!" % (value_key, key, name))
                    case "tags":
                        if not isinstance(value_value, list):
                            raise TypeError("Key \"%s\" of key \"%s\" of key \"types \" of TypedDict \"%s\" is not a list!" % (value_key, key, name))
                        for tag_index, tag_item in enumerate(value_value):
                            if not isinstance(tag_item, str):
                                raise TypeError("Item %i of key \"%s\" of key \"%s\" of key \"types\" of TypedDict \"%s\" is not a str!" % (tag_index, value_key, key, name))
                    case _:
                        raise KeyError("Key \"%s\" of key \"%s\" of \"types\" of TypedDict \"%s\" is not a valid key!" % (value_key, key, name))
            for required_key in ("type",):
                if required_key not in value:
                    raise KeyError("Key \"%s\" of key \"types\" of TypedDict \"%s\" does not have the required key \"%s\"!" % (key, name, required_key))
        if "normalizer" in data and isinstance(data["normalizer"], list):
            if not all(isinstance(item, str) for item in data["normalizer"]):
                raise TypeError("An item of key \"normalizer\" of TypedDict \"%s\" is not a str!" % (name))

        self.name = name
        self.field = "field" if "field" not in data else data["field"]
        self.types_strs = data["types"]
        self.types:dict[str,ComparerTyping.TypedDictTypeFilledTypedDict]|None = None
        self.imports = [] if "imports" not in data else ([data["imports"]] if isinstance(data["imports"], str) else data["imports"])
        self.measure_length = False if "measure_length" not in data else data["measure_length"]
        self.normalizer_strs = None if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"])
        self.print_all = False if "print_all" not in data else data["print_all"]
        self.tags = {key: (value["tags"] if "tags" in value else []) for key, value in self.types_strs.items()}

        self.links_to_other_intermediates:list[Intermediate.Intermediate] = []
        self.parents:list[Intermediate.Intermediate] = []
        self.normalizers:list[NormalizerFunctionIntermediate.NormalizerFunctionIntermediate]|None = None
        self.types_final:dict[tuple[str,type],ComparerSection.ComparerSection|None] = {}
        self.check_types_final:dict[str,tuple[list[type],ComparerIntermediate.ComparerIntermediate|GroupIntermediate.GroupIntermediate|None]] = {}
        self.final:TypedDictComparerSection.TypedDictComparerSection|None = None

        self.children_has_normalizer = False

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
                raise KeyError("Duplicate type \"%s\" of key \"%s\" of TypedDict \"%s\"." % (type_str, key, self.name))
            already_keys.add(type_str)

            if type_str in ComparerTyping.DEFAULT_TYPES:
                types.append(ComparerTyping.DEFAULT_TYPES[type_str])
            else:
                choose_comparer_keys:list[str|int] = ["types", key, "type"] if index is None else ["types", key, "type", index]
                type_intermediate:TypeAliasIntermediate.TypeAliasIntermediate = self.choose_intermediate(type_str, TypeAliasIntermediate.TypeAliasIntermediate, "a TypeAlias", intermediate_comparers, choose_comparer_keys)
                self.links_to_other_intermediates.append(type_intermediate)
                type_intermediate.parents.append(self)
                types.append(type_intermediate)
        return types

    def set_comparer(self, key:str, data:ComparerTyping.TypedDictTypeTypedDict, intermediate_comparers:dict[str,Intermediate.Intermediate]) -> ComparerIntermediate.ComparerIntermediate|GroupIntermediate.GroupIntermediate|None:
        if "comparer" not in data or data["comparer"] is None: return None
        comparer:ComparerIntermediate.ComparerIntermediate|GroupIntermediate.GroupIntermediate = self.choose_intermediate(data["comparer"], (ComparerIntermediate.ComparerIntermediate, GroupIntermediate.GroupIntermediate), "a Comparer or Group", intermediate_comparers, ["types", key, "comparer"])
        self.links_to_other_intermediates.append(comparer)
        comparer.parents.append(self)
        return comparer

    def set(self, intermediate_comparers:dict[str,Intermediate.Intermediate], functions:dict[str,Callable]) -> None:

        for index, imported_comparer_str in enumerate(self.imports):
            comparer:TypedDictComparerIntermediate = self.choose_intermediate(imported_comparer_str, TypedDictComparerIntermediate, "a TypedDict", intermediate_comparers, ["imports", index])
            self.links_to_other_intermediates.append(comparer)
            comparer.parents.append(self)
            for new_key, new_value in comparer.types_strs.items():
                if new_key in self.types_strs: continue
                self.types_strs[new_key] = new_value

        self.types = {}
        for key, data in self.types_strs.items():
            self.types[key] = {
                "comparer": self.set_comparer(key, data, intermediate_comparers),
                "type": self.choose_types(key, data, intermediate_comparers),
            }
        if self.normalizer_strs is None:
            self.normalizers = None
        else:
            self.normalizers:list[NormalizerFunctionIntermediate.NormalizerFunctionIntermediate]|None = [self.choose_intermediate(normalizer_str, NormalizerFunctionIntermediate.NormalizerFunctionIntermediate, "a NormalizerFunction", intermediate_comparers, ["normalizer"]) for normalizer_str in self.normalizer_strs]
            self.links_to_other_intermediates.extend(self.normalizers)
            for normalizer in self.normalizers:
                normalizer.parents.append(self)

    def create_final(self) -> None:
        normalizer_final = None if self.normalizers is None else [cast(Normalizer.Normalizer, normalizer.final) for normalizer in self.normalizers]
        self.final = TypedDictComparerSection.TypedDictComparerSection(
            name=self.field,
            types=self.types_final,
            measure_length=self.measure_length,
            normalizer=normalizer_final,
            print_all=self.print_all,
            children_has_normalizer=self.children_has_normalizer,
        )

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
                        exceptions.append(TypeError("Key \"%s\" of TypedDictComparer \"%s\" accepts type %s, but has a null comparer!" % (key, self.name, type_item.__name__)))
            else:
                if set(key_types) != set(comparer.my_type):
                    my_types = ", ".join(type_item.__name__ for type_item in sorted(key_types, key=lambda x: x.__name__))
                    its_types = ", ".join(type_item.__name__ for type_item in sorted(comparer.my_type, key=lambda x: x.__name__))
                    exceptions.append(TypeError("Key \"%s\" of TypedDictComparer \"%s\" accepts types [%s], but its comparer, \"%s\", only accepts type [%s]!" % (key, self.name, my_types, comparer.name, its_types)))
        return exceptions
