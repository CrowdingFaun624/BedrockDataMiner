from typing import Callable, cast

import Comparison.ComparerImporter.ComparerIntermediate as ComparerIntermediate
import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerImporter.GroupIntermediate as GroupIntermediate
import Comparison.ComparerImporter.NormalizerFunctionIntermediate as NormalizerFunctionIntermediate
import Comparison.ComparerImporter.TypeAliasIntermediate as TypeAliasIntermediate
import Comparison.ListComparerSection as ListComparerSection
import Comparison.Normalizer as Normalizer

class ListComparerIntermediate(ComparerIntermediate.ComparerIntermediate):

    my_type = [list]

    def __init__(self, data:ComparerTyping.ListComparerTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("comparer", (str, type(None)), "a str or None", True),
            ("field", str, "a str", False),
            ("measure_length", bool, "a bool", False),
            ("normalizer", (str, list), "a str or list", False),
            ("ordered", bool, "a bool", False),
            ("print_all", bool, "a bool", False),
            ("print_flat", bool, "a bool", False),
            ("type", str, "a str", True),
            ("types", list, "a list", True),
        ])
        if data["type"] != "List":
            raise ValueError("Key \"type\" of ListComparer \"%s\" is not \"List\"!" % (name))
        if len(data["types"]) == 0:
            raise ValueError("Key \"types\" of ListComparer \"%s\" is empty!" % (name))
        if not all(isinstance(item, str) for item in data["types"]):
            raise TypeError("An item of key \"types\" of ListComparer \"%s\" is not a str!" % (name))
        if "normalizer" in data and isinstance(data["normalizer"], list):
            if not all(isinstance(item, str) for item in data["normalizer"]):
                raise TypeError("An item of key \"normalizer\" of ListComparer \"%s\" is not a str!" % (name))

        self.name = name
        self.comparer_str = data["comparer"]
        self.field = "item" if "field" not in data else data["field"]
        self.measure_length = False if "measure_length" not in data else data["measure_length"]
        self.normalizer_strs = None if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"])
        self.ordered = True if "ordered" not in data else data["ordered"]
        self.print_all = False if "print_all" not in data else data["print_all"]
        self.print_flat = False if "print_flat" not in data else data["print_flat"]
        self.types_strs = data["types"]

        self.comparer:ComparerIntermediate.ComparerIntermediate|GroupIntermediate.GroupIntermediate|None = None
        self.types:list[type|TypeAliasIntermediate.TypeAliasIntermediate]|None = None
        self.links_to_other_intermediates:list[Intermediate.Intermediate] = []
        self.parents:list[Intermediate.Intermediate] = []
        self.normalizers:list[NormalizerFunctionIntermediate.NormalizerFunctionIntermediate]|None = None
        self.types_final:list[type] = []
        self.final:ListComparerSection.ListComparerSection|None = None

        self.children_has_normalizer = False

    def set(self, intermediate_comparers:dict[str,Intermediate.Intermediate], functions:dict[str,Callable]) -> None:
        if self.comparer_str is None:
            self.comparer = None
        else:
            comparer:ComparerIntermediate.ComparerIntermediate|GroupIntermediate.GroupIntermediate = self.choose_intermediate(self.comparer_str, (ComparerIntermediate.ComparerIntermediate, GroupIntermediate.GroupIntermediate), "a Comparer or Group", intermediate_comparers, ["comparer"])
            self.links_to_other_intermediates.append(comparer)
            comparer.parents.append(self)
            self.comparer = comparer
        self.types = []
        for index, type_str in enumerate(self.types_strs):
            if type_str in ComparerTyping.DEFAULT_TYPES:
                self.types.append(ComparerTyping.DEFAULT_TYPES[type_str])
            else:
                type_intermediate:TypeAliasIntermediate.TypeAliasIntermediate = self.choose_intermediate(type_str, TypeAliasIntermediate.TypeAliasIntermediate, "A TypeAlias", intermediate_comparers, ["types", index])
                self.links_to_other_intermediates.append(type_intermediate)
                type_intermediate.parents.append(self)
                self.types.append(type_intermediate)
        if self.normalizer_strs is None:
            self.normalizers = None
        else:
            self.normalizers:list[NormalizerFunctionIntermediate.NormalizerFunctionIntermediate]|None = [self.choose_intermediate(normalizer_str, NormalizerFunctionIntermediate.NormalizerFunctionIntermediate, "a NormalizerFunction", intermediate_comparers, ["normalizer"]) for normalizer_str in self.normalizer_strs]
            self.links_to_other_intermediates.extend(self.normalizers)
            for normalizer in self.normalizers:
                normalizer.parents.append(self)

    def create_final(self) -> None:
        self.types_final:list[type] = []
        assert self.types is not None
        for types_item in self.types:
            if isinstance(types_item, type):
                self.types_final.append(types_item)
            else:
                assert types_item.types is not None
                self.types_final.extend(types_item.types)
        normalizer_final = None if self.normalizers is None else [cast(Normalizer.Normalizer, normalizer.final) for normalizer in self.normalizers]
        self.final = ListComparerSection.ListComparerSection(
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

    def link_finals(self) -> None:
        assert self.final is not None
        if self.comparer is None:
            self.final.comparer = None
        else:
            self.final.comparer = self.comparer.final

    def check(self) -> list[Exception]|None:
        assert self.final is not None
        self.final.check_initialization_parameters()
        if self.comparer is None:
            for value_type in self.types_final:
                if value_type in ComparerTyping.REQUIRES_COMPARER_TYPES:
                    return [TypeError("ListComparer \"%s\" accepts type %s, but has a null comparer!" % (self.name, value_type.__name__))]
        else:
            for value_type in self.types_final:
                if value_type not in self.comparer.my_type:
                    its_types = ", ".join(type_item.__name__ for type_item in self.comparer.my_type)
                    return [TypeError("ListComparer \"%s\" accepts type %s, but its comparer, \"%s\", only accepts type [%s]!" % (self.name, value_type.__name__, self.comparer.name, its_types))]
