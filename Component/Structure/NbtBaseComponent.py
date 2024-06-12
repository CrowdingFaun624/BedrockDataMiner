from typing import Literal

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Pattern as Pattern
import Component.Structure.AbstractGroupComponent as AbstractGroupComponent
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.StructroidComponentField as StructroidComponentField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.GroupComponent as GroupComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.NbtBaseStructure as NbtBaseStructure
import Utilities.Exceptions as Exceptions
import Utilities.Nbt.Endianness as Endianness
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

COMPONENT_REQUEST_PROPERTIES:Pattern.Pattern[StructureComponent.StructureComponent|GroupComponent.GroupComponent] = Pattern.Pattern([{"is_nbt_tag": True, "is_structure": True}, {"is_group": True}])

class NbtBaseComponent(AbstractGroupComponent.AbstractGroupComponent[NbtBaseStructure.NbtBaseStructure]):

    class_name_article = "an NbtBase"
    class_name = "NbtBase"
    my_capabilities = Capabilities.Capabilities(is_group=True, is_nbt_base=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or StructroidComponent", True, (str, dict)),
        TypeVerifier.TypedDictKeyTypeVerifier("endianness", "a str", True, TypeVerifier.EnumTypeVerifier(("big", "little"))),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def __init__(self, data:ComponentTyping.NbtBaseTypedDict, name: str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data, name)

        self.endianness:Literal["big", "little"] = data["endianness"]
        self.final_structure:NbtBaseStructure.NbtBaseStructure|None=None
        self.children_has_normalizer = True

        self.subcomponent_field = StructroidComponentField.StructroidComponentField(data["subcomponent"], ["subcomponent"], pattern=COMPONENT_REQUEST_PROPERTIES)
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.normalizer_field:NormalizerListField.NormalizerListField = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.types_field.verify_with(self.subcomponent_field)
        self.fields.extend([self.subcomponent_field, self.types_field, self.normalizer_field])

    def get_subcomponents(self) -> list[Component.Component]:
        return [self.subcomponent_field.get_component()]

    def get_endianness(self, endianness:Literal["big", "little"]) -> Endianness.End:
        match endianness:
            case "big": return Endianness.End.BIG
            case "little": return Endianness.End.LITTLE

    def create_final(self) -> None:
        super().create_final()
        self.final_structure = NbtBaseStructure.NbtBaseStructure(
            name = self.name,
            endianness=self.get_endianness(self.endianness),
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )
        self.final = {}

    def get_final_structure(self) -> NbtBaseStructure.NbtBaseStructure:
        if self.final_structure is None:
            raise Exceptions.AttributeNoneError("final_structure", self)
        return self.final_structure

    def link_finals(self) -> None:
        super().link_finals()
        final = self.get_final()
        final_structure = self.get_final_structure()
        types = self.types_field.get_types()
        self.my_type = set(types)
        final_structure.link_substructures(
            structure=self.subcomponent_field.get_final(),
            types=types,
            normalizer=self.normalizer_field.get_finals(),
        )
        final[NbtReader.NbtBytes] = final_structure
        for my_type in self.my_type: final[my_type] = final_structure
