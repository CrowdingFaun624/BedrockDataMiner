from typing import Callable

import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerImporter.ComparerIntermediate as ComparerIntermediate
import Comparison.ComparerImporter.TypeAliasIntermediate as TypeAliasIntermediate
import Comparison.ComparerSection as ComparerSection

class GroupIntermediate(Intermediate.Intermediate):

    def __init__(self, data:ComparerTyping.GroupTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("type", str, "a str", True),
            ("types", dict, "a dict", True),
        ])
        if data["type"] != "Group":
            raise ValueError("Key \"type\" of Group \"%s\" is not \"Group\"!" % (name))
        if len(data["types"]) == 0:
            raise ValueError("Key \"types\" of Group \"%s\" is empty!" % (name))
        if not all(isinstance(key, str) for key in data["types"].keys()):
            raise TypeError("A key of key \"types\" in Group \"%s\" is not a str!" % (name))
        if not all(isinstance(value, str) or value is None for value in data["types"].values()):
            raise TypeError("A value of key \"types\" in Group \"%s\" is not a str or None!" % (name))

        self.name = name
        self.types_strs = data["types"]

        self.types:list[tuple[type|TypeAliasIntermediate.TypeAliasIntermediate,ComparerIntermediate.ComparerIntermediate|None]]|None = None
        self.links_to_other_intermediates:list[Intermediate.Intermediate] = []
        self.parents:list[Intermediate.Intermediate] = []
        self.my_type:set[type] = set()
        self.check_types_final:list[tuple[list[type], ComparerIntermediate.ComparerIntermediate|None]]|None = None
        self.final:dict[type,ComparerSection.ComparerSection|None]|None = None

        self.children_has_normalizer = False

    def set(self, intermediate_comparers:dict[str,Intermediate.Intermediate], functions:dict[str,Callable]) -> None:
        self.types = []
        already_types:set[str] = set()
        for type_str, comparer_str in self.types_strs.items():
            comparer:ComparerIntermediate.ComparerIntermediate|None
            comparer_type:TypeAliasIntermediate.TypeAliasIntermediate|type
            if type_str in already_types:
                raise KeyError("Duplicate type \"%s\" of Group \"%s\"." % (type_str, self.name))
            already_types.add(type_str)
            if type_str in ComparerTyping.DEFAULT_TYPES:
                comparer_type = ComparerTyping.DEFAULT_TYPES[type_str]
                self.my_type.add(comparer_type)
            else:
                comparer_type = self.choose_intermediate(type_str, TypeAliasIntermediate.TypeAliasIntermediate, "a TypeAlias", intermediate_comparers, ["types", type_str])
                assert isinstance(comparer_type, TypeAliasIntermediate.TypeAliasIntermediate)
                self.links_to_other_intermediates.append(comparer_type)
                comparer_type.parents.append(self)
                assert comparer_type.types is not None
                self.my_type.update(comparer_type.types)
            if comparer_str is None:
                comparer = None
            else:
                comparer = self.choose_intermediate(comparer_str, ComparerIntermediate.ComparerIntermediate, "a Comparer", intermediate_comparers, ["types", type_str])
                assert comparer is not None
                self.links_to_other_intermediates.append(comparer)
                comparer.parents.append(self)
            self.types.append((comparer_type, comparer))

    def create_final(self) -> None:
        self.final = {}

    def link_finals(self) -> None:
        assert self.types is not None
        assert self.final is not None
        self.check_types_final = []
        for comparer_type, comparer_intermediate in self.types:
            valid_types:list[type]
            if isinstance(comparer_type, type):
                valid_types = [comparer_type]
            elif isinstance(comparer_type, TypeAliasIntermediate.TypeAliasIntermediate):
                assert comparer_type.types is not None
                valid_types = comparer_type.types
            if comparer_intermediate is None:
                comparer_final = None
            else:
                comparer_final = comparer_intermediate.final
            for valid_type in valid_types:
                self.final[valid_type] = comparer_final
            self.check_types_final.append((valid_types, comparer_intermediate))

    def check(self) -> list[Exception]|None:
        assert self.check_types_final is not None
        for index, (types, comparer) in enumerate(self.check_types_final):
            if comparer is None:
                for type_item in types:
                    if type_item in ComparerTyping.REQUIRES_COMPARER_TYPES:
                        return [TypeError("Item %i of Group \"%s\" accepts type %s, but has a null comparer!" % (index, self.name, type_item.__name__))]
            else:
                for type_item in types:
                    if type_item not in comparer.my_type:
                        its_types = ", ".join(its_type.__name__ for its_type in comparer.my_type)
                        return [TypeError("Item %i of Group \"%s\" accepts type %s, but its comparer, \"%s\", only accepts type [%s]!" % (index, self.name, type_item.__name__, comparer.name, its_types))]
