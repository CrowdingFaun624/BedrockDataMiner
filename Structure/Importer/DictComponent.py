from typing import Callable, cast

import Structure.DictStructure as DictStructure
import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.GroupComponent as GroupComponent
import Structure.Importer.ImporterConfig as ImporterConfig
import Structure.Importer.NormalizerComponent as NormalizerComponent
import Structure.Importer.StructureComponent as StructureComponent
import Structure.Importer.TagComponent as TagComponent
import Structure.Importer.TypeAliasComponent as TypeAliasComponent
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Utilities.TypeVerifier as TypeVerifier

COMPONENT_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_group": True}, {"is_structure": True}])
NORMALIZER_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_normalizer": True}])
TAG_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_tag": True}])
TYPE_ALIAS_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_type_alias": True}])

class DictComponent(StructureComponent.StructureComponent):

    class_name_article = "a Dict"
    class_name = "Dict"

    my_type = [dict]

    my_properties = ComponentCapabilities.Capabilities(has_keys=True, is_structure=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("comparison_move_function", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("detect_key_moves", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
    )

    def __init__(self, data:ComponentTyping.DictComponentTypedDict, name:str, index:int) -> None:
        self.verify_arguments(data, name)

        self.name = name
        self.subcomponent_str = data["subcomponent"]
        self.comparison_move_function_str = data.get("comparison_move_function", None)
        self.detect_key_moves = data.get("detect_key_moves", False)
        self.field = data.get("field", "field")
        self.measure_length = data.get("measure_length", False)
        self.normalizer_strs = None if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"])
        self.print_all = data.get("print_all", False)
        self.types_strs = data["types"]
        self.tags_strs = data.get("tags", [])

        self.subcomponent:StructureComponent.StructureComponent|GroupComponent.GroupComponent|None = None
        self.comparison_move_function:Callable|None = None
        self.normalizers:list[NormalizerComponent.NormalizerComponent]|None = None
        self.types:list[type|TypeAliasComponent.TypeAliasComponent] = []
        self.tags:list[TagComponent.TagComponent]|None = None
        self.links_to_other_components:list[Component.Component] = []
        self.parents:list[Component.Component] = []
        self.types_final:tuple[type,...]|None = None
        self.final:DictStructure.DictStructure|None = None
        self.tags_final:list[str] = []
        self.children_tags:set[str] = set()

        self.children_has_normalizer = False

    def choose_types(self, key:str, types_strs:list[str], components:dict[str,Component.Component]) -> list[type|TypeAliasComponent.TypeAliasComponent]:
        types:list[type|TypeAliasComponent.TypeAliasComponent] = []
        already_types:set[str] = set()
        for type_str in types_strs:
            if type_str in already_types:
                raise KeyError("Duplicate type \"%s\" of key \"%s\" of %s \"%s\"." % (type_str, key, self.class_name, self.name))
            already_types.add(type_str)
            if type_str in ComponentTyping.DEFAULT_TYPES:
                types.append(ComponentTyping.DEFAULT_TYPES[type_str])
            else:
                type_alias = self.choose_component(type_str, TYPE_ALIAS_REQUEST_PROPERTIES, components, [key])
                self.links_to_other_components.append(type_alias)
                types.append(type_alias)
        return types

    def set_subcomponent(self, components:dict[str,Component.Component], subcomponent_str:str|None) -> StructureComponent.StructureComponent|GroupComponent.GroupComponent|None:
        if subcomponent_str is None:
            return None
        else:
            subcomponent:StructureComponent.StructureComponent|GroupComponent.GroupComponent = self.choose_component(subcomponent_str, COMPONENT_REQUEST_PROPERTIES, components, ["subcomponent"])
            self.link_components(subcomponent)
            return subcomponent

    def set_comparison_move_function(self, functions:dict[str,Callable], comparison_move_function_str:str|None) -> Callable|None:
        if comparison_move_function_str is None:
            return None
        else:
            if comparison_move_function_str not in functions:
                raise KeyError("Function \"%s\", referenced in key \"comparison_move_function\" of %s \"%s\", does not exist!" % (comparison_move_function_str, self.class_name, self.name))
            return functions[comparison_move_function_str]

    def set_normalizers(self, components:dict[str,Component.Component], normalizer_strs:list[str]|None) -> list[NormalizerComponent.NormalizerComponent]|None:
        if normalizer_strs is None:
            return None
        else:
            normalizers:list[NormalizerComponent.NormalizerComponent] = [self.choose_component(normalizer_str, NORMALIZER_REQUEST_PROPERTIES, components, ["normalizer"]) for normalizer_str in normalizer_strs]
            self.link_components(normalizers)
            return normalizers

    def set_tags(self, tags_strs:list[str], components:dict[str,Component.Component]) -> list[TagComponent.TagComponent]:
        tags:list[TagComponent.TagComponent] = []
        for index, tag_str in enumerate(tags_strs):
            tags.append(self.choose_component(tag_str, TAG_REQUEST_PROPERTIES, components, ["tags", index]))
        self.link_components(tags)
        self.children_tags.update(tags_strs)
        return tags

    def set_component(self, components:dict[str,Component.Component], functions:dict[str,Callable]) -> None:
        self.subcomponent = self.set_subcomponent(components, self.subcomponent_str)
        self.comparison_move_function = self.set_comparison_move_function(functions, self.comparison_move_function_str)
        self.types = self.choose_types("types", self.types_strs, components)
        self.tags = self.set_tags(self.tags_strs, components)
        self.normalizers = self.set_normalizers(components, self.normalizer_strs)

    def create_final_get_types_final(self, types:list[type|TypeAliasComponent.TypeAliasComponent]) -> tuple[type,...]:
        '''Expands a list of types and TypeAliases into just a tuple of types.'''
        output:list[type] = []
        for types_item in types:
            if isinstance(types_item, type):
                output.append(types_item)
            else:
                assert types_item.types is not None
                output.extend(types_item.types)
        return tuple(output)

    def create_final_get_normalizers(self, normalizers:list[NormalizerComponent.NormalizerComponent]|None) -> list[Normalizer.Normalizer]|None:
        return None if normalizers is None else [cast(Normalizer.Normalizer, normalizer.final) for normalizer in normalizers]

    def create_final_get_final(self, normalizer_final:list[Normalizer.Normalizer]|None) -> DictStructure.DictStructure:
        return DictStructure.DictStructure(
            name=self.name,
            field=self.field,
            structure=None,
            types=self.types_final,
            detect_key_moves=self.detect_key_moves,
            comparison_move_function=self.comparison_move_function,
            measure_length=self.measure_length,
            normalizer=normalizer_final,
            print_all=self.print_all,
            tags=self.tags_final,
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )

    def create_final(self) -> None:
        self.types_final = self.create_final_get_types_final(self.types)
        normalizer_final = self.create_final_get_normalizers(self.normalizers)
        self.final = self.create_final_get_final(normalizer_final)

    def link_finals(self) -> None:
        assert self.final is not None
        if self.subcomponent is None:
            self.final.structure = None
        else:
            assert self.subcomponent.final is not None
            self.final.structure = cast(Structure.Structure|None|dict[type,Structure.Structure|None], self.subcomponent.final)
        
        assert self.tags is not None
        for tag in self.tags:
            self.tags_final.append(tag.name)

    def check(self, config:ImporterConfig.ImporterConfig) -> list[Exception]:
        assert self.final is not None
        assert self.types_final is not None
        self.final.check_initialization_parameters()
        if self.subcomponent is None:
            for value_type in self.types_final:
                if value_type in ComponentTyping.REQUIRES_SUBCOMPONENT_TYPES:
                    return [TypeError("%s \"%s\" accepts type %s, but has a null Subcomponent!" % (self.class_name, self.name, value_type.__name__))]
        else:
            if set(self.types_final) != set(self.subcomponent.my_type):
                my_types = ", ".join(type_item.__name__ for type_item in self.types_final)
                its_types = ", ".join(type_item.__name__ for type_item in self.subcomponent.my_type)
                return [TypeError("%s \"%s\" accepts types [%s], but its Subcomponent, \"%s\", only accepts type [%s]!" % (self.class_name, self.name, my_types, self.subcomponent.name, its_types))]
        return []
