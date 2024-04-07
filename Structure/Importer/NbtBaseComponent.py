from typing import Callable, cast

import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.GroupComponent as GroupComponent
import Structure.Importer.NormalizerComponent as NormalizerComponent
import Structure.Importer.StructureComponent as StructureComponent
import Structure.Importer.TypeAliasComponent as TypeAliasComponent
import Structure.NbtBaseStructure as NbtBaseStructure
import Structure.Normalizer as Normalizer
import Utilities.Nbt.Endianness as Endianness
import Utilities.Nbt.NbtTypes as NbtTypes
import Utilities.TypeVerifier as TypeVerifier

COMPONENT_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_nbt_tag": True, "is_structure": True}, {"is_group": True}])
NORMALIZER_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_normalizer": True}])
TYPE_ALIAS_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_type_alias": True}])

class NbtBaseComponent(StructureComponent.StructureComponent):

    class_name_article = "an NbtBase"
    class_name = "NbtBase"

    my_properties = ComponentCapabilities.Capabilities(is_structure=True, is_nbt_base=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("endianness", "a str", True, TypeVerifier.EnumTypeVerifier(("big", "little"))),
            TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
            TypeVerifier.TypedDictKeyTypeVerifier("types", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("index", "an int", True, int),
    )

    def __init__(self, data:ComponentTyping.NbtBaseTypedDict, name: str, index: int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index}, ["%s \"%s\"" % (self.class_name, name)])

        self.name = name
        self.subcomponent_str = data["subcomponent"]
        self.endianness = data["endianness"]
        self.types_strs = data["types"]
        self.normalizer_strs = None if "normalizer" not in data else ([data["normalizer"]] if isinstance(data["normalizer"], str) else data["normalizer"])

        self.links_to_other_components:list[Component.Component] = []
        self.parents:list[Component.Component] = []
        self.children_has_normalizer = True # All NbtBases have built-in normalizers that unpack the NBT
        self.types:list[type|TypeAliasComponent.TypeAliasComponent]|None = None
        self.types_final:list[type] = []
        self.final:NbtBaseStructure.NbtBaseStructure|None = None
        self.subcomponent:StructureComponent.StructureComponent|GroupComponent.GroupComponent|None = None

    def set_component(self, components: dict[str, Component.Component], functions: dict[str, Callable]) -> None:
        self.subcomponent:StructureComponent.StructureComponent|GroupComponent.GroupComponent|None = self.choose_component(self.subcomponent_str, COMPONENT_REQUEST_PROPERTIES, components, ["subcomponent"])
        assert self.subcomponent is not None
        self.links_to_other_components.append(self.subcomponent)
        self.subcomponent.parents.append(self)

        self.types = []
        for index, type_str in enumerate(self.types_strs):
            if type_str in ComponentTyping.DEFAULT_TYPES:
                self.types.append(ComponentTyping.DEFAULT_TYPES[type_str])
            else:
                type_alias_component:TypeAliasComponent.TypeAliasComponent = self.choose_component(type_str, TYPE_ALIAS_REQUEST_PROPERTIES, components, ["types", index])
                self.links_to_other_components.append(type_alias_component)
                type_alias_component.parents.append(self)
                self.types.append(type_alias_component)
        if self.normalizer_strs is None:
            self.normalizers = None
        else:
            self.normalizers:list[NormalizerComponent.NormalizerComponent]|None = [self.choose_component(normalizer_str, NORMALIZER_REQUEST_PROPERTIES, components, ["normalizer"]) for normalizer_str in self.normalizer_strs]
            self.links_to_other_components.extend(self.normalizers)
            for normalizer in self.normalizers:
                normalizer.parents.append(self)

    def create_final_get_types_final(self, types:list[type|TypeAliasComponent.TypeAliasComponent]|None) -> list[type]:
        types_final:list[type] = []
        assert types is not None
        for types_item in types:
            if isinstance(types_item, type):
                types_final.append(types_item)
            else:
                assert types_item.types is not None
                types_final.extend(types_item.types)
        return types_final

    def create_final_get_normalizers(self, normalizers:list[NormalizerComponent.NormalizerComponent]|None) -> list[Normalizer.Normalizer]|None:
        return None if self.normalizers is None else [cast(Normalizer.Normalizer, normalizer.final) for normalizer in self.normalizers]

    def get_endianness(self, endianness:str) -> Endianness.End:
        match endianness:
            case "big": return Endianness.End.BIG
            case "little": return Endianness.End.LITTLE
            case _: raise ValueError("Invalid endianness \"%s\"!" % endianness)

    def create_final_get_final(self, normalizers_final:list[Normalizer.Normalizer]|None) -> NbtBaseStructure.NbtBaseStructure:
        return NbtBaseStructure.NbtBaseStructure(
            name = self.name,
            structure = None,
            endianness=self.get_endianness(self.endianness),
            types = tuple(self.types_final),
            normalizer = normalizers_final,
            children_has_normalizer=self.children_has_normalizer,
        )

    def create_final(self) -> None:
        self.types_final = self.create_final_get_types_final(self.types)
        self.my_type = self.types_final
        normalizers_final = self.create_final_get_normalizers(self.normalizers)
        self.final = self.create_final_get_final(normalizers_final)
    
    def link_finals(self) -> None:
        assert self.final is not None
        assert self.subcomponent is not None
        assert self.subcomponent.final is not None
        self.final.structure = self.subcomponent.final
    
    def check(self) -> list[Exception] | None:
        assert self.final is not None
        assert self.subcomponent is not None
        self.final.check_initialization_parameters()
        for value_type in self.types_final:
            if not issubclass(value_type, NbtTypes.TAG):
                return [TypeError("%s \"%s\" cannot except non-NbtTag type %s!" % (self.class_name, self.name, value_type.__name__))]
            if value_type not in self.subcomponent.my_type:
                its_types = ", ".join(type_item.__name__ for type_item in self.subcomponent.my_type)
                return [TypeError("%s \"%s\" accepts type %s, but its Subcomponent, \"%s\", only accepts type [%s]!" % (self.class_name, self.name, value_type.__name__, self.subcomponent.name, its_types))]
