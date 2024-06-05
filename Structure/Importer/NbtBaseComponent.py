from typing import Literal

import Structure.Importer.AbstractGroupComponent as AbstractGroupComponent
import Structure.Importer.Capabilities as Capabilities
import Structure.Importer.Component as Component
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.NormalizerListField as NormalizerListField
import Structure.Importer.Field.StructroidComponentField as StructroidComponentField
import Structure.Importer.Field.TypeListField as TypeListField
import Structure.Importer.GroupComponent as GroupComponent
import Structure.Importer.Pattern
import Structure.Importer.StructureComponent as StructureComponent
import Structure.NbtBaseStructure as NbtBaseStructure
import Utilities.Exceptions as Exceptions
import Utilities.Nbt.Endianness as Endianness
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

COMPONENT_REQUEST_PROPERTIES:Structure.Importer.Pattern.Pattern[StructureComponent.StructureComponent|GroupComponent.GroupComponent] = Structure.Importer.Pattern.Pattern([{"is_nbt_tag": True, "is_structure": True}, {"is_group": True}])

class NbtBaseComponent(AbstractGroupComponent.AbstractGroupComponent):

    class_name_article = "an NbtBase"
    class_name = "NbtBase"
    my_capabilities = Capabilities.Capabilities(is_group=True, is_nbt_base=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("endianness", "a str", True, TypeVerifier.EnumTypeVerifier(("big", "little"))),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def __init__(self, data:ComponentTyping.NbtBaseTypedDict, name: str) -> None:
        super().__init__(name)
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
