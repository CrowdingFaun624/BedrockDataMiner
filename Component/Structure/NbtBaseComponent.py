from typing import Literal

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
import Component.Structure.Field.StructureComponentField as StructureComponentField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.StructureComponent as StructureComponent
import Structure.NbtBaseStructure as NbtBaseStructure
import Utilities.Nbt.Endianness as Endianness
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class NbtBaseComponent(StructureComponent.StructureComponent[NbtBaseStructure.NbtBaseStructure]):

    class_name_article = "an NbtBase"
    class_name = "NbtBase"
    children_has_normalizer_default = True
    my_capabilities = Capabilities.Capabilities(is_group=True, is_nbt_base=True, is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", "a str or null", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("endianness", "a str", True, TypeVerifier.EnumTypeVerifier(("big", "little"))),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or StructureComponent", True, (str, dict)),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def __init__(self, data:ComponentTyping.NbtBaseTypedDict, name: str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data)

        self.endianness:Literal["big", "little"] = data["endianness"]
        self.final_structure:NbtBaseStructure.NbtBaseStructure|None=None

        self.subcomponent_field = StructureComponentField.StructureComponentField(data["subcomponent"], ["subcomponent"])
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", None), data.get("delegate_arguments", {}), ["delegate"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.normalizer_field = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.post_normalizer_field = NormalizerListField.NormalizerListField(data.get("post_normalizer", []), ["post_normalizer"])
        self.types_field.verify_with(self.subcomponent_field)
        self.types_field.must_be(StructureComponent.NBT_TYPES)
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", []), ["pre_normalized_types"])
        self.fields.extend([self.subcomponent_field, self.delegate_field, self.types_field, self.normalizer_field, self.pre_normalized_types_field, self.post_normalizer_field])

    def get_subcomponents(self) -> list[Component.Component]:
        return [self.subcomponent_field.get_component()]

    def get_endianness(self, endianness:Literal["big", "little"]) -> Endianness.End:
        match endianness:
            case "big": return Endianness.End.BIG
            case "little": return Endianness.End.LITTLE

    def create_final(self) -> None:
        super().create_final()
        self.final = NbtBaseStructure.NbtBaseStructure(
            name = self.name,
            endianness=self.get_endianness(self.endianness),
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )

    def link_finals(self) -> None:
        super().link_finals()
        types = self.types_field.get_types()
        self.my_type = set(types)
        self.my_type.add(NbtReader.NbtBytes)
        self.get_final().link_substructures(
            structure=self.subcomponent_field.get_final(),
            delegate=self.delegate_field.create_delegate(self.get_final()),
            types=types,
            normalizer=self.normalizer_field.get_finals(),
            post_normalizer=self.post_normalizer_field.get_finals(),
            pre_normalized_types=self.pre_normalized_types_field.get_types() if len(self.pre_normalized_types_field.get_types()) != 0 else types,
        )
