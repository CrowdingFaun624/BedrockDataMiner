from typing import Callable, cast, Generator, Iterable

import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.GroupComponent as GroupComponent
import Structure.Importer.ImporterConfig as ImporterConfig
import Structure.Importer.NormalizerComponent as NormalizerComponent
import Structure.Importer.StructureComponent as StructureComponent
import Structure.Importer.TagComponent as TagComponent
import Structure.Importer.TypeAliasComponent as TypeAliasComponent
import Structure.KeymapStructure as KeymapStructure
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Utilities.TypeVerifier as TypeVerifier

COMPONENT_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_group": True}, {"is_structure": True}])
IMPORTABLE_KEYS_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"has_importable_keys": True}])
NORMALIZER_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_normalizer": True}])
TAG_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_tag": True}])
TYPE_ALIAS_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_type_alias": True}])

empty_set_of_strings:set[str] = set()

class KeymapComponent(StructureComponent.StructureComponent):

    class_name_article = "a Keymap"
    class_name = "Keymap"

    my_type = [dict]

    my_properties = ComponentCapabilities.Capabilities(has_importable_keys=True, has_keys=True, is_structure=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("imports", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("keys", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or None", False, (str, type(None))),
            TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        ), "a dict", "a str", "a dict")),
    )

    def __init__(self, data:ComponentTyping.KeymapComponentTypedDict, name:str) -> None:
        self.verify_arguments(data, name)

        self.name = name
        self.field = data.get("field", "field")
        self.keys_strs = data["keys"]
        self.keys:dict[str,ComponentTyping.KeymapKeyFilledTypedDict]|None = None
        self.imports = [] if "imports" not in data else ([data["imports"]] if isinstance(data["imports"], str) else data["imports"])
        self.measure_length = data.get("measure_length", False)
        self.normalizer_strs:list[str]|None = None if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"])
        self.print_all = data.get("print_all", False)
        self.tags_for_all_strs = data.get("tags", [])
        self.tags_strs = {key: (value["tags"] if "tags" in value else []) for key, value in self.keys_strs.items()}

        self.links_to_other_components:list[Component.Component] = []
        self.parents:list[Component.Component] = []
        self.normalizers:list[NormalizerComponent.NormalizerComponent]|None = None
        self.tags:dict[str,list[TagComponent.TagComponent]]|None = None
        self.tags_for_all:list[TagComponent.TagComponent]|None = None
        self.keys_final:dict[tuple[str,type],Structure.Structure|None] = {}
        self.check_keys_final:dict[str,tuple[list[type],StructureComponent.StructureComponent|GroupComponent.GroupComponent|None]] = {}
        self.final:KeymapStructure.KeymapStructure|None = None
        self.tags_final:dict[str,list[str]] = {}

        self.children_has_normalizer = self.children_has_normalizer_default
        self.children_tags:set[str] = set()

    def choose_types_type_iterator(self, data:ComponentTyping.KeymapKeyTypedDict) -> Generator[tuple[int|None, str], None, None]:
        '''Yields the index of the type_str and the type_str, or None and the type_str if it is not a list'''
        if isinstance(data["type"], str):
            yield (None, data["type"])
        else:
            yield from enumerate(data["type"])

    def choose_types(self, key:str, data:ComponentTyping.KeymapKeyTypedDict, components:dict[str,Component.Component]) -> list[type|TypeAliasComponent.TypeAliasComponent]:
        types:list[type|TypeAliasComponent.TypeAliasComponent] = []
        already_keys:set[str] = set()
        for index, type_str in self.choose_types_type_iterator(data):
            if type_str in already_keys:
                raise KeyError("Duplicate type \"%s\" of key \"%s\" of %s \"%s\"." % (type_str, key, self.class_name, self.name))
            already_keys.add(type_str)

            if type_str in ComponentTyping.DEFAULT_TYPES:
                types.append(ComponentTyping.DEFAULT_TYPES[type_str])
            else:
                choose_component_keys:list[str|int] = ["types", key, "type"] if index is None else ["types", key, "type", index]
                type_alias_component:TypeAliasComponent.TypeAliasComponent = self.choose_component(type_str, TYPE_ALIAS_REQUEST_PROPERTIES, components, choose_component_keys)
                self.links_to_other_components.append(type_alias_component)
                type_alias_component.parents.append(self)
                types.append(type_alias_component)
        return types

    def set_imports(self, components:dict[str,Component.Component], imports:list[str]) -> list["KeymapComponent"]:
        return [self.choose_component(imported_component_str, IMPORTABLE_KEYS_REQUEST_PROPERTIES, components, ["imports", index]) for index, imported_component_str in enumerate(imports)]

    def add_import_to_self(self, imports:list["KeymapComponent"]) -> None:
        for component in imports:
            for new_key, new_value in component.keys_strs.items():
                if new_key in self.keys_strs: continue
                self.keys_strs[new_key] = new_value

    def set_subcomponent(self, key:str, data:ComponentTyping.KeymapKeyTypedDict, components:dict[str,Component.Component]) -> StructureComponent.StructureComponent|GroupComponent.GroupComponent|None:
        if "subcomponent" not in data or data["subcomponent"] is None: return None
        subcomponent:StructureComponent.StructureComponent|GroupComponent.GroupComponent = self.choose_component(data["subcomponent"], COMPONENT_REQUEST_PROPERTIES, components, ["keys", key, "subcomponent"])
        self.links_to_other_components.append(subcomponent)
        subcomponent.parents.append(self)
        return subcomponent

    def set_type(self, key:str, data:ComponentTyping.KeymapKeyTypedDict, components:dict[str,Component.Component]) -> ComponentTyping.KeymapKeyFilledTypedDict:
        return {
            "subcomponent": self.set_subcomponent(key, data, components),
            "type": self.choose_types(key, data, components),
        }

    def set_types(self, components:dict[str,Component.Component], types_strs:dict[str,ComponentTyping.KeymapKeyTypedDict]) -> dict[str,ComponentTyping.KeymapKeyFilledTypedDict]:
        return {key: self.set_type(key, data, components) for key, data in types_strs.items()}

    def set_normalizers(self, components:dict[str,Component.Component], normalizer_strs:list[str]|None) -> list[NormalizerComponent.NormalizerComponent]|None:
        if normalizer_strs is None:
            return None
        else:
            normalizers:list[NormalizerComponent.NormalizerComponent] = [self.choose_component(normalizer_str, NORMALIZER_REQUEST_PROPERTIES, components, ["normalizer"]) for normalizer_str in normalizer_strs]
            return normalizers

    def set_tags(self, components:dict[str,Component.Component], tags_strs:dict[str,list[str]], tags_for_all_strs:list[str]) -> tuple[dict[str,list[TagComponent.TagComponent]], list[TagComponent.TagComponent]]:
        tags:dict[str,list[TagComponent.TagComponent]] = {}
        for key, key_tags_strs in tags_strs.items():
            tag_components:list[TagComponent.TagComponent] = []
            for index, key_tag_str in enumerate(key_tags_strs):
                tag_components.append(self.choose_component(key_tag_str, TAG_REQUEST_PROPERTIES, components, ["keys", key, "tags", index]))
            self.link_components(tag_components)
            tags[key] = tag_components
            self.children_tags.update(key_tags_strs)
        tags_for_all:list[TagComponent.TagComponent] = []
        for index, tag_str in enumerate(tags_for_all_strs):
            tags_for_all.append(self.choose_component(tag_str, TAG_REQUEST_PROPERTIES, components, ["tags", index]))
        self.link_components(tags_for_all)
        self.children_tags.update(tags_for_all_strs)
        return tags, tags_for_all

    def set_component(self, components:dict[str,Component.Component], functions:dict[str,Callable]) -> None:
        imports = self.set_imports(components, self.imports)
        self.link_components(imports)
        self.add_import_to_self(imports)

        self.keys = self.set_types(components, self.keys_strs)
        self.normalizers = self.set_normalizers(components, self.normalizer_strs)
        self.tags, self.tags_for_all = self.set_tags(components, self.tags_strs, self.tags_for_all_strs)
        if self.normalizers is not None:
            self.link_components(self.normalizers)

    def create_final_get_final_normalizers(self) -> list[Normalizer.Normalizer]|None:
        return None if self.normalizers is None else [cast(Normalizer.Normalizer, normalizer.final) for normalizer in self.normalizers]

    def create_final_get_final(self, normalizer_final:list[Normalizer.Normalizer]|None) -> KeymapStructure.KeymapStructure:
        return KeymapStructure.KeymapStructure(
            name=self.name,
            field=self.field,
            keys=self.keys_final,
            measure_length=self.measure_length,
            normalizer=normalizer_final,
            print_all=self.print_all,
            tags=self.tags_final,
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )

    def create_final(self) -> None:
        normalizer_final = self.create_final_get_final_normalizers()
        self.final = self.create_final_get_final(normalizer_final)

    def expand_types(self, types:Iterable[type|TypeAliasComponent.TypeAliasComponent]) -> Generator[type,None,None]:
        for item in types:
            if isinstance(item, type): yield item
            else:
                assert item.types is not None
                yield from item.types

    def link_finals(self) -> None:
        assert self.keys is not None
        for types_key, types_value in self.keys.items():
            subcomponent = types_value["subcomponent"]
            if isinstance(subcomponent, GroupComponent.GroupComponent):
                assert subcomponent.final is not None
                for group_type, group_subcomponent in subcomponent.final.items():
                    self.keys_final[types_key, group_type] = group_subcomponent
                self.check_keys_final[types_key] = (list(self.expand_types(types_value["type"])), subcomponent)
            else:
                key_types = list(self.expand_types(types_value["type"]))
                structure = (subcomponent.final if subcomponent is not None else None)
                for key_type in key_types:
                    self.keys_final[types_key, key_type] = structure
                self.check_keys_final[types_key] = (list(self.expand_types(types_value["type"])), subcomponent)
        
        assert self.tags is not None
        assert self.tags_for_all is not None
        tags_for_all_set = {tag.name for tag in self.tags_for_all}
        for key, tags in self.tags.items():
            self.tags_final[key] = sorted({tag.name for tag in tags} | tags_for_all_set)

    def check(self, config:ImporterConfig.ImporterConfig) -> list[Exception]:
        assert self.final is not None
        self.final.check_initialization_parameters()
        exceptions:list[Exception] = []
        for key, (key_types, subcomponent) in self.check_keys_final.items():
            if subcomponent is None:
                for type_item in key_types:
                    if type_item in ComponentTyping.REQUIRES_SUBCOMPONENT_TYPES:
                        exceptions.append(TypeError("Key \"%s\" of %s \"%s\" accepts type %s, but has a null Subcomponent!" % (key, self.class_name, self.name, type_item.__name__)))
            else:
                if set(key_types) != set(subcomponent.my_type):
                    my_types = ", ".join(type_item.__name__ for type_item in sorted(key_types, key=lambda x: x.__name__))
                    its_types = ", ".join(type_item.__name__ for type_item in sorted(subcomponent.my_type, key=lambda x: x.__name__))
                    exceptions.append(TypeError("Key \"%s\" of %s \"%s\" accepts types [%s], but its Subcomponent, \"%s\", only accepts type [%s]!" % (key, self.class_name, self.name, my_types, subcomponent.name, its_types)))
        return exceptions

    def finalize_finals(self) -> None:
        assert self.final is not None
        self.final.finalize()
