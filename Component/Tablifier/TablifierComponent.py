import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.DataMiner.Field.DataMinerCollectionField as DataMinerCollectionField
import Component.Structure.Field.StructureField as StructureField
import Component.Version.Field.VersionProviderField as VersionProviderField
import Tablifier.Tablifier as Tablifier
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class TablifierComponent(Component.Component[Tablifier.Tablifier]):

    class_name_article = "a Tablifier"
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

    def __init__(self, data: ComponentTyping.TablifierTypedDict, name: str, component_group: str, index: int | None) -> None:
        super().__init__(data, name, component_group, index)

        self.file_name = data["file_name"]

        self.dataminer_collection_field = DataMinerCollectionField.DataMinerCollectionField(data["dataminer_collection"], ["dataminer_collection"])
        self.structure_field = StructureField.StructureField(data["structure"], ["structure"])
        self.version_provider_field = VersionProviderField.VersionProviderField(data["version_provider"], ["version_provider"])
        self.fields.extend([self.dataminer_collection_field, self.structure_field, self.version_provider_field])

    def create_final(self) -> None:
        super().create_final()
        self.final = Tablifier.Tablifier(
            name=self.name,
            file_name=self.file_name,
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.get_final().link_finals(
            structure=self.structure_field.get_final(),
            dataminer_collection=self.dataminer_collection_field.get_final(),
            version_provider=self.version_provider_field.get_final()(),
        )
        return exceptions
