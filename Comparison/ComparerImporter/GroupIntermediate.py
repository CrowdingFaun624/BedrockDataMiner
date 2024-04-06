from typing import Callable

import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerImporter.IntermediateCapabilities as IntermediateCapabilities
import Comparison.ComparerImporter.ComparerIntermediate as ComparerIntermediate
import Comparison.ComparerImporter.TypeAliasIntermediate as TypeAliasIntermediate
import Comparison.ComparerSection as ComparerSection
import Utilities.TypeVerifier as TypeVerifier

COMPARER_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"is_comparer": True}])
TYPE_ALIAS_REQUEST_PROPERTIES = IntermediateCapabilities.CapabilitiesPattern([{"is_type_alias": True}])

class GroupIntermediate(Intermediate.Intermediate):

    class_name_article = "a Group"
    class_name = "Group"

    my_properties = IntermediateCapabilities.Capabilities(is_group=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
            TypeVerifier.TypedDictKeyTypeVerifier("types", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, (str, type(None)), "a dict", "a str", "a str or None")),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("index", "an int", True, int),
    )

    def __init__(self, data:ComparerTyping.GroupTypedDict, name:str, index:int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index}, ["%s \"%s\"" % (self.class_name, name)])

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
                raise KeyError("Duplicate type \"%s\" of %s \"%s\"." % (type_str, self.class_name, self.name))
            already_types.add(type_str)
            if type_str in ComparerTyping.DEFAULT_TYPES:
                comparer_type = ComparerTyping.DEFAULT_TYPES[type_str]
                self.my_type.add(comparer_type)
            else:
                comparer_type = self.choose_intermediate(type_str, TYPE_ALIAS_REQUEST_PROPERTIES, intermediate_comparers, ["types", type_str])
                assert isinstance(comparer_type, TypeAliasIntermediate.TypeAliasIntermediate)
                self.links_to_other_intermediates.append(comparer_type)
                comparer_type.parents.append(self)
                assert comparer_type.types is not None
                self.my_type.update(comparer_type.types)
            if comparer_str is None:
                comparer = None
            else:
                comparer = self.choose_intermediate(comparer_str, COMPARER_REQUEST_PROPERTIES, intermediate_comparers, ["types", type_str])
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
                        return [TypeError("Item %i of %s \"%s\" accepts type %s, but has a null comparer!" % (index, self.class_name, self.name, type_item.__name__))]
            else:
                for type_item in types:
                    if type_item not in comparer.my_type:
                        its_types = ", ".join(its_type.__name__ for its_type in comparer.my_type)
                        return [TypeError("Item %i of %s \"%s\" accepts type %s, but its comparer, \"%s\", only accepts type [%s]!" % (index, self.class_name, self.name, type_item.__name__, comparer.name, its_types))]
