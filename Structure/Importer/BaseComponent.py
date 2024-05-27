from typing import cast

import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.ComponentField as ComponentField
import Structure.Importer.Field.OptionalComponentField as OptionalComponentField
import Structure.Importer.NormalizerComponent as NormalizerComponent
import Structure.Importer.StructureComponent as StructureComponent
import Structure.Structure as Structure
import Structure.StructureBase as StructureBase
import Utilities.TypeVerifier as TypeVerifier

COMPONENT_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_structure": True}])
NORMALIZER_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_normalizer": True}])

class BaseComponent(Component.Component):

    class_name_article = "a Base"
    class_name = "Base"
    my_properties = ComponentCapabilities.Capabilities(is_base=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("imports", "a list", False, TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("from", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("components", "a dict", True, TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
                TypeVerifier.TypedDictKeyTypeVerifier("component", "a str", True, str),
                TypeVerifier.TypedDictKeyTypeVerifier("as", "a str", False, str),
            ), list, "a dict", "a list")),
        ), list, "a dict", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
    )

    def __init__(self, data:ComponentTyping.BaseComponentTypedDict, name:str) -> None:
        super().__init__(name)
        self.verify_arguments(data, name)

        self.structure_name = data["name"]
        self.imports = data.get("imports", None)
        self.final:StructureBase.StructureBase|None = None

        self.subcomponent_field:ComponentField.ComponentField[StructureComponent.StructureComponent] = ComponentField.ComponentField(data["subcomponent"], COMPONENT_REQUEST_PROPERTIES, ["subcomponent"])
        self.normalizer_field:OptionalComponentField.OptionalComponentField[NormalizerComponent.NormalizerComponent] = OptionalComponentField.OptionalComponentField(data.get("normalizer", None), NORMALIZER_REQUEST_PROPERTIES, ["normalizer"])
        self.post_normalizer_field:OptionalComponentField.OptionalComponentField[NormalizerComponent.NormalizerComponent] = OptionalComponentField.OptionalComponentField(data.get("post_normalizer", None), NORMALIZER_REQUEST_PROPERTIES, ["post_normalizer"])
        self.fields.extend([self.subcomponent_field, self.normalizer_field, self.post_normalizer_field])

    def create_final(self) -> None:
        self.final = StructureBase.StructureBase(
            component_name=self.name,
            structure_name=self.structure_name,
            children_tags=self.children_tags,
        )

    def link_finals(self) -> None:
        super().link_finals()
        assert self.final is not None
        normalizer_component = self.normalizer_field.get_component()
        post_normalizer_component = self.post_normalizer_field.get_component()
        self.final.link_substructures(
            structure=cast(Structure.Structure, self.subcomponent_field.get_component().final),
            normalizer=None if normalizer_component is None else normalizer_component.final,
            post_normalizer=None if post_normalizer_component is None else post_normalizer_component.final
        )
