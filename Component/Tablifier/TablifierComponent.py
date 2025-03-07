import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Dataminer.AbstractDataminerCollectionComponent as AbstractDataminerCollectionComponent
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Field.ScriptedClassField as ScriptedClassField
import Component.Structure.BaseComponent as BaseComponent
import Tablifier.Tablifier as Tablifier
import Utilities.TypeVerifier as TypeVerifier


class TablifierComponent(Component.Component[Tablifier.Tablifier]):

    class_name = "Tablifier"
    my_capabilities = Capabilities.Capabilities(is_tablifier=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("dataminer_collection", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("file_name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("structure", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("version_provider", "a str", True, str),
    )

    __slots__ = (
        "dataminer_collection_field",
        "file_name",
        "structure_field",
        "version_provider_field",
    )

    def initialize_fields(self, data: ComponentTyping.TablifierTypedDict) -> list[Field.Field]:
        self.file_name = data["file_name"]

        self.dataminer_collection_field = ComponentField.ComponentField(data["dataminer_collection"], AbstractDataminerCollectionComponent.ABSTRACT_DATAMINER_COLLECTION_PATTERN, ["dataminer_collection"], allow_inline=Field.InlinePermissions.reference, assume_component_group="dataminer_collections")
        self.structure_field = ComponentField.ComponentField(data["structure"], BaseComponent.STRUCTURE_BASE_PATTERN, ["structure"], allow_inline=Field.InlinePermissions.reference)
        self.version_provider_field = ScriptedClassField.ScriptedClassField(data["version_provider"], lambda script_set_set_set: script_set_set_set.version_provider_classes, ["version_provider"])
        return [self.dataminer_collection_field, self.structure_field, self.version_provider_field]

    def create_final(self) -> Tablifier.Tablifier:
        return Tablifier.Tablifier(
            name=self.name,
            file_name=self.file_name,
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.final.link_finals(
            structure=self.structure_field.subcomponent.final,
            dataminer_collection=self.dataminer_collection_field.subcomponent.final,
            version_provider=self.version_provider_field.object_class(self.domain),
        )
        return exceptions
