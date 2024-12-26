from typing import TYPE_CHECKING, cast

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.DataMiner.Field.OptionalDataMinerTypeField as OptionalDataMinerTypeField
import Component.Field.ComponentField as ComponentField
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.FieldListField as FieldListField
import Component.Pattern as Pattern
import Component.Serializer.Field.SerializerDictField as SerializerDictField
import Component.Version.Field.OptionalVersionField as OptionalVersionField
import DataMiner.DataMinerSettings as DataMinerSettings
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

if TYPE_CHECKING:
    import Component.DataMiner.AbstractDataMinerCollectionComponent as AbstractDataMinerCollectionComponent
    import Component.DataMiner.DataMinerCollectionComponent as DataMinerCollectionComponent
    import Component.Version.VersionFileTypeComponent as VersionFileTypeComponent

DEPENDENCY_PATTERN:Pattern.Pattern["AbstractDataMinerCollectionComponent.AbstractDataMinerCollectionComponent"] = Pattern.Pattern([{"is_dataminer_collection": True}])
VERSION_FILE_TYPE_PATTERN:Pattern.Pattern["VersionFileTypeComponent.VersionFileTypeComponent"] = Pattern.Pattern([{"is_version_file_type": True}])

class DataMinerSettingsComponent(Component.Component[DataMinerSettings.DataMinerSettings]):

    class_name_article = "a DataMinerSettings"
    class_name = "DataMinerSettings"
    my_capabilities = Capabilities.Capabilities(is_dataminer_settings=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("dependencies", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("files", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("new", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("old", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("serializer", "a str or dict", False, TypeVerifier.UnionTypeVerifier("a str or dict", str, TypeVerifier.DictTypeVerifier(dict, str, str, "a dict", "a str", "a str"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    def __init__(self, data:ComponentTyping.DataMinerSettingsTypedDict, name: str, component_group: str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)

        self.files_field_exists = "files" in data
        self.arguments = data.get("arguments", {})

        self.new_field = OptionalVersionField.OptionalVersionField(data["new"], ["new"])
        self.old_field = OptionalVersionField.OptionalVersionField(data["old"], ["old"])
        self.files_field = ComponentListField.ComponentListField(data.get("files", []), VERSION_FILE_TYPE_PATTERN, ["files"], allow_inline=Field.InlinePermissions.reference)
        self.serializer_field = SerializerDictField.SerializerDictField((data["serializer"] if isinstance(data["serializer"], dict) else {"main": data["serializer"]}) if "serializer" in data else {}, ["serializer"])
        self.dataminer_field = OptionalDataMinerTypeField.OptionalDataMinerTypeField(data["name"], ["name"])
        self.dependencies_field = FieldListField.FieldListField([
            ComponentField.ComponentField(
                dependency_name,
                DEPENDENCY_PATTERN,
                ["dependencies", index],
                allow_inline=Field.InlinePermissions.reference
            ) for index, dependency_name in enumerate(data.get("dependencies", []))
        ], ["dependencies"])
        self.fields.extend([self.new_field, self.old_field, self.files_field, self.serializer_field, self.dataminer_field, self.dependencies_field])

    def create_final(self) -> None:
        super().create_final()
        self.final = DataMinerSettings.DataMinerSettings(
            kwargs=self.arguments
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        parent = cast("DataMinerCollectionComponent.DataMinerCollectionComponent", self.get_inline_parent())
        exceptions.extend(self.get_final().link_subcomponents(
            file_name=parent.file_name,
            name=parent.name,
            structure=parent.structure_field.get_final(),
            dataminer_class=self.dataminer_field.get_final(),
            serializers=self.serializer_field.get_final(),
            dependencies=list(self.dependencies_field.map(lambda dataminer_collection_component: dataminer_collection_component.get_component().get_final())),
            start_version=self.old_field.get_final(),
            end_version=self.new_field.get_final(),
            version_file_types=list(self.files_field.map(lambda version_file_type_field: version_file_type_field.get_final()))
        ))
        return exceptions

    def check(self) -> list[Exception]:
        exceptions = super().check()
        if self.dataminer_field.exists():
            if not self.files_field_exists:
                exceptions.append(Exceptions.DataMinerCollectionFileError(False, self, "when \"name\" is not null"))
        else:
            if self.files_field_exists:
                exceptions.append(Exceptions.DataMinerCollectionFileError(True, self, "when \"name\" is null"))
        return exceptions
