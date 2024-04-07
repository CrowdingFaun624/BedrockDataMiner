from typing import Callable, cast, Generator, Iterable

import Structure.Importer.StructureComponent as StructureComponent
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.GroupComponent as GroupComponent
import Structure.Importer.NormalizerComponent as NormalizerComponent
import Structure.Importer.TypeAliasComponent as TypeAliasComponent
import Structure.Structure as Structure
import Structure.Normalizer as Normalizer
import Structure.KeymapStructure as KeymapStructure
import Utilities.TypeVerifier as TypeVerifier

COMPONENT_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_group": True}, {"is_structure": True}])
IMPORTABLE_KEYS_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"has_importable_keys": True}])
NORMALIZER_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_normalizer": True}])
TYPE_ALIAS_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_type_alias": True}])

class KeymapComponent(StructureComponent.StructureComponent):

    class_name_article = "a Keymap"
    class_name = "Keymap"

    my_type = [dict]

    my_properties = ComponentCapabilities.Capabilities(has_importable_keys=True, is_structure=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
            TypeVerifier.TypedDictKeyTypeVerifier("imports", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier("Keymap")),
            TypeVerifier.TypedDictKeyTypeVerifier("keys", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.TypedDictTypeVerifier(
                TypeVerifier.TypedDictKeyTypeVerifier("type", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
                TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or None", False, (str, type(None))),
                TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
            ), "a dict", "a str", "a dict")),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("index", "an int", True, int),
    )

    def __init__(self, data:ComponentTyping.KeymapComponentTypedDict, name:str, index:int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index}, ["%s \"%s\"" % (self.class_name, name)])

        self.name = name
        self.field = data.get("field", "field")
        self.types_strs = data["keys"]
        self.types:dict[str,ComponentTyping.KeymapKeyFilledTypedDict]|None = None
        self.imports = [] if "imports" not in data else ([data["imports"]] if isinstance(data["imports"], str) else data["imports"])
        self.measure_length = data.get("measure_length", False)
        self.normalizer_strs:list[str]|None = None if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"])
        self.print_all = data.get("print_all", False)
        self.tags = {key: (value["tags"] if "tags" in value else []) for key, value in self.types_strs.items()}

        self.links_to_other_components:list[Component.Component] = []
        self.parents:list[Component.Component] = []
        self.normalizers:list[NormalizerComponent.NormalizerComponent]|None = None
        self.keys_final:dict[tuple[str,type],Structure.Structure|None] = {}
        self.check_keys_final:dict[str,tuple[list[type],StructureComponent.StructureComponent|GroupComponent.GroupComponent|None]] = {}
        self.final:KeymapStructure.KeymapStructure|None = None

        self.children_has_normalizer = self.children_has_normalizer_default

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
            for new_key, new_value in component.types_strs.items():
                if new_key in self.types_strs: continue
                self.types_strs[new_key] = new_value

    def set_component(self, key:str, data:ComponentTyping.KeymapKeyTypedDict, components:dict[str,Component.Component]) -> StructureComponent.StructureComponent|GroupComponent.GroupComponent|None:
        if "subcomponent" not in data or data["subcomponent"] is None: return None
        subcomponent:StructureComponent.StructureComponent|GroupComponent.GroupComponent = self.choose_component(data["subcomponent"], COMPONENT_REQUEST_PROPERTIES, components, ["keys", key, "subcomponent"])
        self.links_to_other_components.append(subcomponent)
        subcomponent.parents.append(self)
        return subcomponent

    def set_type(self, key:str, data:ComponentTyping.KeymapKeyTypedDict, components:dict[str,Component.Component]) -> ComponentTyping.KeymapKeyFilledTypedDict:
        return {
            "subcomponent": self.set_component(key, data, components),
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

    def set(self, components:dict[str,Component.Component], functions:dict[str,Callable]) -> None:
        imports = self.set_imports(components, self.imports)
        self.link_components(imports)
        self.add_import_to_self(imports)

        self.types = self.set_types(components, self.types_strs)
        self.normalizers = self.set_normalizers(components, self.normalizer_strs)
        if self.normalizers is not None:
            self.link_components(self.normalizers)

    def create_final_get_final_normalizers(self) -> list[Normalizer.Normalizer]|None:
        return None if self.normalizers is None else [cast(Normalizer.Normalizer, normalizer.final) for normalizer in self.normalizers]

    def create_final_get_final(self, normalizer_final:list[Normalizer.Normalizer]|None) -> KeymapStructure.KeymapStructure:
        return KeymapStructure.KeymapStructure(
            name=self.field,
            types=self.keys_final,
            measure_length=self.measure_length,
            normalizer=normalizer_final,
            print_all=self.print_all,
            children_has_normalizer=self.children_has_normalizer,
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
        assert self.types is not None
        for types_key, types_value in self.types.items():
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

    def check(self) -> list[Exception]|None:
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
