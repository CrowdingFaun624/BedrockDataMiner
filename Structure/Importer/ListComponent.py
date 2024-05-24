from typing import Callable, cast

import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.GroupComponent as GroupComponent
import Structure.Importer.ImporterConfig as ImporterConfig
import Structure.Importer.NormalizerComponent as NormalizerComponent
import Structure.Importer.StructureComponent as StructureComponent
import Structure.Importer.TagComponent as TagComponent
import Structure.Importer.TypeAliasComponent as TypeAliasComponent
import Structure.ListStructure as ListStructure
import Structure.Normalizer as Normalizer
import Utilities.TypeVerifier as TypeVerifier

COMPONENT_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_group": True}, {"is_structure": True}])
NORMALIZER_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_normalizer": True}])
TAG_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_tag": True}])
TYPE_ALIAS_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_type_alias": True}])

class ListComponent(StructureComponent.StructureComponent):

    class_name_article = "a List"
    class_name = "List"

    my_type = [list]

    my_properties = ComponentCapabilities.Capabilities(is_structure=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("ordered", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("print_flat", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
    )

    def __init__(self, data:ComponentTyping.ListComponentTypedDict, name:str, index:int) -> None:
        self.verify_arguments(data, name)

        self.name = name
        self.subcomponent_str = data["subcomponent"]
        self.field = data.get("field", "item")
        self.measure_length = data.get("measure_length", False)
        self.normalizer_strs = None if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"])
        self.ordered = data.get("ordered", True)
        self.print_all = data.get("print_all", False)
        self.print_flat = data.get("print_flat", False)
        self.tags_strs = data.get("tags", [])
        self.types_strs = data["types"]

        self.subcomponent:StructureComponent.StructureComponent|GroupComponent.GroupComponent|None = None
        self.types:list[type|TypeAliasComponent.TypeAliasComponent]|None = None
        self.links_to_other_components:list[Component.Component] = []
        self.parents:list[Component.Component] = []
        self.normalizers:list[NormalizerComponent.NormalizerComponent]|None = None
        self.tags:list[TagComponent.TagComponent]|None = []
        self.types_final:list[type] = []
        self.tags_final:list[str] = []
        self.final:ListStructure.ListStructure|None = None

        self.children_has_normalizer = False
        self.children_tags:set[str] = set()

    def set_sub_component(self, components:dict[str,Component.Component], subcomponent_str:str|None) -> StructureComponent.StructureComponent|GroupComponent.GroupComponent|None:
        if subcomponent_str is None:
            return None
        else:
            subcomponent = self.choose_component(subcomponent_str, COMPONENT_REQUEST_PROPERTIES, components, ["subcomponent"])
            self.link_components(subcomponent)
            return subcomponent

    def set_types(self, components:dict[str,Component.Component], types_strs:list[str]) -> list[type|TypeAliasComponent.TypeAliasComponent]:
        types:list[type|TypeAliasComponent.TypeAliasComponent] = []
        for index, type_str in enumerate(types_strs):
            if type_str in ComponentTyping.DEFAULT_TYPES:
                types.append(ComponentTyping.DEFAULT_TYPES[type_str])
            else:
                type_alias_component:TypeAliasComponent.TypeAliasComponent = self.choose_component(type_str, TYPE_ALIAS_REQUEST_PROPERTIES, components, ["types", index])
                types.append(type_alias_component)
                self.link_components(type_alias_component)
        return types

    def set_normalizers(self, components:dict[str,Component.Component], normalizer_strs:list[str]|None) -> list[NormalizerComponent.NormalizerComponent]|None:
        if normalizer_strs is None:
            return None
        else:
            normalizers:list[NormalizerComponent.NormalizerComponent] = [self.choose_component(normalizer_str, NORMALIZER_REQUEST_PROPERTIES, components, ["normalizer"]) for normalizer_str in normalizer_strs]
            self.link_components(normalizers)
            return normalizers

    def set_tags(self, components:dict[str,Component.Component], tags_strs:list[str]) -> list[TagComponent.TagComponent]:
        tags:list[TagComponent.TagComponent] = []
        for index, tag_str in enumerate(tags_strs):
            tags.append(self.choose_component(tag_str, TAG_REQUEST_PROPERTIES, components, ["tags", index]))
        self.link_components(tags)
        self.children_tags.update(tags_strs)
        return tags

    def set_component(self, components:dict[str,Component.Component], functions:dict[str,Callable]) -> None:
        self.subcomponent = self.set_sub_component(components, self.subcomponent_str)
        self.types = self.set_types(components, self.types_strs)
        self.tags = self.set_tags(components, self.tags_strs)
        self.normalizers = self.set_normalizers(components, self.normalizer_strs)

    def create_final_get_final_types(self, types:list[type|TypeAliasComponent.TypeAliasComponent]|None) -> list[type]:
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

    def create_final_get_final(self, normalizer_final:list[Normalizer.Normalizer]|None) -> ListStructure.ListStructure:
        return ListStructure.ListStructure(
            name=self.name,
            field=self.field,
            structure=None,
            types=tuple(self.types_final),
            print_flat=self.print_flat,
            print_all=self.print_all,
            measure_length=self.measure_length,
            normalizer=normalizer_final,
            ordered=self.ordered,
            tags=self.tags_final,
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )

    def create_final(self) -> None:
        self.types_final:list[type] = self.create_final_get_final_types(self.types)
        normalizer_final = self.create_final_get_final_normalizers()
        self.final = self.create_final_get_final(normalizer_final)

    def link_finals(self) -> None:
        assert self.final is not None
        if self.subcomponent is None:
            self.final.structure = None
        else:
            self.final.structure = self.subcomponent.final

        assert self.tags is not None
        for tag in self.tags:
            self.tags_final.append(tag.name)

    def check_components(self) -> list[Exception]:
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

    def check(self, config:ImporterConfig.ImporterConfig) -> list[Exception]:
        assert self.final is not None
        exceptions:list[Exception] = []
        self.final.check_initialization_parameters()
        exceptions.extend(self.check_components())
        return exceptions
