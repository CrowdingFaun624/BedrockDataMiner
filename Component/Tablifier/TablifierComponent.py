from typing import Sequence

from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import TablifierTypedDict
from Component.Dataminer.AbstractDataminerCollectionComponent import (
    ABSTRACT_DATAMINER_COLLECTION_PATTERN,
)
from Component.Field.ComponentField import ComponentField
from Component.Field.Field import Field, InlinePermissions
from Component.Field.ScriptedClassField import ScriptedClassField
from Component.Structure.StructureBaseComponent import STRUCTURE_BASE_PATTERN
from Tablifier.Tablifier import Tablifier
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class TablifierComponent(Component[Tablifier]):

    class_name = "Tablifier"
    my_capabilities = Capabilities()
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("dataminer_collection", True, str),
        TypedDictKeyTypeVerifier("file_name", True, str),
        TypedDictKeyTypeVerifier("structure", True, str),
        TypedDictKeyTypeVerifier("type", False, str),
        TypedDictKeyTypeVerifier("version_provider", True, str),
    )

    @property
    def assume_used(self) -> bool:
        return True

    __slots__ = (
        "dataminer_collection_field",
        "file_name",
        "structure_field",
        "version_provider_field",
    )

    def initialize_fields(self, data: TablifierTypedDict) -> Sequence[Field]:
        self.file_name = data["file_name"]

        self.dataminer_collection_field = ComponentField(data["dataminer_collection"], ABSTRACT_DATAMINER_COLLECTION_PATTERN, ("dataminer_collection",), allow_inline=InlinePermissions.reference)
        self.structure_field = ComponentField(data["structure"], STRUCTURE_BASE_PATTERN, ("structure",), allow_inline=InlinePermissions.reference)
        self.version_provider_field = ScriptedClassField(data["version_provider"], lambda script_set_set_set: script_set_set_set.version_provider_classes, ("version_provider",))
        return (self.dataminer_collection_field, self.structure_field, self.version_provider_field)

    def create_final(self, trace:Trace) -> Tablifier:
        return Tablifier(
            name=self.name,
            full_name=self.full_name,
            file_name=self.file_name,
        )

    def link_finals(self, trace:Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_finals(
                structure=self.structure_field.subcomponent.final,
                dataminer_collection=self.dataminer_collection_field.subcomponent.final,
                version_provider=self.version_provider_field.object_class(self.domain),
            )
