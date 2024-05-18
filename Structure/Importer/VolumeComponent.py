from typing import Any, Callable, cast

import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.GroupComponent as GroupComponent
import Structure.Importer.NormalizerComponent as NormalizerComponent
import Structure.Importer.StructureComponent as StructureComponent
import Structure.Importer.TagComponent as TagComponent
import Structure.Importer.TypeAliasComponent as TypeAliasComponent
import Structure.Normalizer as Normalizer
import Structure.VolumeStructure as VolumeStructure
import Structure.Importer.ImporterConfig as ImporterConfig
import Utilities.TypeVerifier as TypeVerifier

COMPONENT_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"has_keys": True}])
NORMALIZER_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_normalizer": True}])
TAG_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_tag": True}])
TYPE_ALIAS_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_type_alias": True}])

class VolumeComponent(GroupComponent.GroupComponent):

    class_name_article = "a Volume"
    class_name = "Volume"
    my_type = {tuple}

    my_properties = ComponentCapabilities.Capabilities(is_group=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
            TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("position_key", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("print_additional_data", "a bool", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("state_key", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or None", True, (str, type(None))),
            TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
            TypeVerifier.TypedDictKeyTypeVerifier("this_type", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
            TypeVerifier.TypedDictKeyTypeVerifier("types", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("index", "an int", True, int),
    )

    def __init__(self, data:ComponentTyping.VolumeTypedDict, name: str, index: int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index}, ["%s \"%s\"" % (self.class_name, name)])

        self.name = name
        self.field = data.get("field", "block")
        self.normalizer_strs = None if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"])
        self.position_key = data["position_key"]
        self.print_additional_data = data.get("print_additional_data", True)
        self.state_key = data["state_key"]
        self.subcomponent_str = data["subcomponent"]
        self.tags_strs = data.get("tags", [])
        self.this_type_str = data["this_type"]
        self.types_strs = data["types"]

        self.children_has_normalizer = True # has to turn into tuple that the thing recognizes.
        self.children_tags:set[str] = set()
        self.links_to_other_components:list[Component.Component] = []
        self.parents:list[Component.Component] = []

        self.subcomponent:StructureComponent.StructureComponent|None
        self.this_type:type|TypeAliasComponent.TypeAliasComponent|None=None
        self.this_type_final:list[type]|None=None
        self.types:list[type|TypeAliasComponent.TypeAliasComponent]|None=None
        self.normalizers:list[NormalizerComponent.NormalizerComponent]|None=None
        self.tags:list[TagComponent.TagComponent]|None=None
        self.final:dict[type,VolumeStructure.VolumeStructure]|None=None
        self.final_structure:VolumeStructure.VolumeStructure|None=None
        self.types_final:list[type]=[]
        self.tags_final:list[str]=[]
        # self.my_type:list[type]=[]

    def set_sub_component(self, components:dict[str, Component.Component], subcomponent_str:str|None) -> StructureComponent.StructureComponent|None:
        if subcomponent_str is None:
            return None
        else:
            subcomponent = self.choose_component(subcomponent_str, COMPONENT_REQUEST_PROPERTIES, components, ["subcomponent"])
            self.link_components(subcomponent)
            return subcomponent

    def set_types(self, components:dict[str, Component.Component], types_strs:list[str]) -> list[type|TypeAliasComponent.TypeAliasComponent]:
        types:list[type|TypeAliasComponent.TypeAliasComponent] = []
        for index, type_str in enumerate(types_strs):
            if type_str in ComponentTyping.DEFAULT_TYPES:
                types.append(ComponentTyping.DEFAULT_TYPES[type_str])
            else:
                type_alias_component:TypeAliasComponent.TypeAliasComponent = self.choose_component(type_str, TYPE_ALIAS_REQUEST_PROPERTIES, components, ["types", index])
                types.append(type_alias_component)
                self.link_components(type_alias_component)
        if self.this_type_str in ComponentTyping.DEFAULT_TYPES:
            self.this_type = ComponentTyping.DEFAULT_TYPES[self.this_type_str]
        else:
            self.this_type = self.choose_component(type_str, TYPE_ALIAS_REQUEST_PROPERTIES, components, ["this_type"])
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

    def set_component(self, components: dict[str, Component.Component], functions: dict[str, Callable[..., Any]]) -> None:
        self.subcomponent = self.set_sub_component(components, self.subcomponent_str)
        self.types = self.set_types(components, self.types_strs)
        self.normalizers = self.set_normalizers(components, self.normalizer_strs)
        self.tags = self.set_tags(components, self.tags_strs)

    def create_final_get_final_types(self, types:list[type|TypeAliasComponent.TypeAliasComponent]|None) -> tuple[list[type],list[type]]:
        types_final:list[type] = []
        assert types is not None
        for types_item in types:
            if isinstance(types_item, type):
                types_final.append(types_item)
            else:
                assert types_item.types is not None
                types_final.extend(types_item.types)
        assert self.this_type is not None
        if isinstance(self.this_type, type):
            this_type_final = [self.this_type]
        else:
            assert self.this_type.types is not None
            this_type_final = self.this_type.types
        return types_final, this_type_final

    def create_final_get_final_normalizers(self) -> list[Normalizer.Normalizer]|None:
        return None if self.normalizers is None else [cast(Normalizer.Normalizer, normalizer.final) for normalizer in self.normalizers]

    def create_final_get_final(self, normalizer_final:list[Normalizer.Normalizer]|None, my_types:list[type]) -> tuple[dict[type,VolumeStructure.VolumeStructure],VolumeStructure.VolumeStructure]:
        final = VolumeStructure.VolumeStructure(
            name=self.name,
            field=self.field,
            position_key=self.position_key,
            state_key=self.state_key,
            structure=None,
            print_additional_data=self.print_additional_data,
            tags=self.tags_final,
            normalizer=normalizer_final,
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )
        output:dict[type,VolumeStructure.VolumeStructure] = {tuple: final}
        for my_type in my_types: output[my_type] = final
        return output, final

    def create_final(self) -> None:
        self.types_final, self.this_type_final = self.create_final_get_final_types(self.types)
        normalizer_final = self.create_final_get_final_normalizers()
        self.final, self.final_structure = self.create_final_get_final(normalizer_final, self.this_type_final)

    def link_finals(self) -> None:
        assert self.final_structure is not None
        if self.subcomponent is None:
            self.final_structure.structure = None
        else:
            self.final_structure.structure = self.subcomponent.final

        assert self.tags is not None
        for tag in self.tags:
            self.tags_final.append(tag.name)

    def check_components(self) -> list[Exception]:
        exceptions:list[Exception] = []
        if self.subcomponent is None:
            pass
        else:
            if set(self.types_final) != set(self.subcomponent.my_type):
                my_types = ", ".join(type_item.__name__ for type_item in self.types_final)
                its_types = ", ".join(type_item.__name__ for type_item in self.subcomponent.my_type)
                exceptions.append(TypeError("%s \"%s\" accepts types [%s], but its Subcomponent, \"%s\", only accepts type [%s]!" % (self.class_name, self.name, my_types, self.subcomponent.name, its_types)))
        return exceptions

    def check(self, config:ImporterConfig.ImporterConfig) -> list[Exception]:
        assert self.final_structure is not None
        exceptions:list[Exception] = []
        self.final_structure.check_initialization_parameters()
        exceptions.extend(self.check_components())
        return exceptions
