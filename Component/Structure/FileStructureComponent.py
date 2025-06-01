from typing import Sequence

import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Serializer.SerializerComponent as SerializerComponent
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.PassthroughStructureComponent as PassthroughStructureComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.StructureTypes.FileStructure as FileStructure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier


class FileStructureComponent(PassthroughStructureComponent.PassthroughStructureComponent[FileStructure.FileStructure]):

    __slots__ = (
        "content_types_field",
        "file_types_field",
        "serializer_field",
        "structure_field",
    )

    class_name = "File"
    structure_type = FileStructure.FileStructure
    type_verifier = PassthroughStructureComponent.PassthroughStructureComponent.type_verifier.extend(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("content_types", True, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("file_types", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("serializer", True, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("structure", True, (str, dict, type(None))),
    ))

    def initialize_fields(self, data: ComponentTyping.FileStructureTypedDict) -> Sequence[Field.Field]:
        fields = list(super().initialize_fields(data))

        self.file_types_field = TypeListField.TypeListField(data.get("file_types", "abstract_file"), ("file_types",)).must_be(self.domain.type_stuff.file_types).make_default(self.pre_normalized_types_field)
        self.structure_field = ComponentField.OptionalComponentField(data["structure"], StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("structure",))
        self.content_types_field = TypeListField.TypeListField(data["content_types"], ("content_types",)).verify_with(self.structure_field).add_to_set(self.my_type)
        self.serializer_field = ComponentField.OptionalComponentField(data["serializer"], SerializerComponent.SERIALIZER_PATTERN, ("serializer",), assume_component_group="serializers")

        fields.extend((self.file_types_field, self.structure_field, self.content_types_field, self.serializer_field))
        return fields

    def link_finals(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_file_structure(
                content_types=self.content_types_field.types,
                file_types=self.file_types_field.types,
                serializer=self.serializer_field.map(lambda subcomponent: subcomponent.final),
                structure=self.structure_field.map(lambda subcomponent: subcomponent.final),
            )
