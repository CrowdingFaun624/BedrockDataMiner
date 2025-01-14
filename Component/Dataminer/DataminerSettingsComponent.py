from typing import TYPE_CHECKING, cast

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Dataminer.Field.OptionalDataminerTypeField as OptionalDataminerTypeField
import Component.Field.ComponentField as ComponentField
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.FieldListField as FieldListField
import Component.Pattern as Pattern
import Component.Serializer.Field.SerializerDictField as SerializerDictField
import Component.Version.Field.OptionalVersionField as OptionalVersionField
import Dataminer.DataminerSettings as DataminerSettings
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier

if TYPE_CHECKING:
    import Component.Dataminer.AbstractDataminerCollectionComponent as AbstractDataminerCollectionComponent
    import Component.Dataminer.DataminerCollectionComponent as DataminerCollectionComponent
    import Component.Version.VersionFileTypeComponent as VersionFileTypeComponent

DEPENDENCY_PATTERN:Pattern.Pattern["AbstractDataminerCollectionComponent.AbstractDataminerCollectionComponent"] = Pattern.Pattern("is_dataminer_collection")
VERSION_FILE_TYPE_PATTERN:Pattern.Pattern["VersionFileTypeComponent.VersionFileTypeComponent"] = Pattern.Pattern("is_version_file_type")

class DataminerSettingsComponent(Component.Component[DataminerSettings.DataminerSettings]):

    class_name_article = "a DataminerSettings"
    class_name = "DataminerSettings"
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

    __slots__ = (
        "arguments",
        "dataminer_field",
        "dependencies_field",
        "files_field",
        "files_field_exists",
        "new_field",
        "old_field",
        "serializer_field",
    )

    def initialize_fields(self, data: ComponentTyping.DataminerSettingsTypedDict) -> list[Field.Field]:
        self.files_field_exists = "files" in data
        self.arguments = data.get("arguments", {})

        self.new_field = OptionalVersionField.OptionalVersionField(data["new"], ["new"])
        self.old_field = OptionalVersionField.OptionalVersionField(data["old"], ["old"])
        self.files_field = ComponentListField.ComponentListField(data.get("files", []), VERSION_FILE_TYPE_PATTERN, ["files"], allow_inline=Field.InlinePermissions.reference, assume_component_group="version_file_types")
        self.serializer_field = SerializerDictField.SerializerDictField((data["serializer"] if isinstance(data["serializer"], dict) else {"main": data["serializer"]}) if "serializer" in data else {}, ["serializer"])
        self.dataminer_field = OptionalDataminerTypeField.OptionalDataminerTypeField(data["name"], ["name"])
        self.dependencies_field = FieldListField.FieldListField([
            ComponentField.ComponentField(
                dependency_name,
                DEPENDENCY_PATTERN,
                ["dependencies", index],
                allow_inline=Field.InlinePermissions.reference
            ) for index, dependency_name in enumerate(data.get("dependencies", []))
        ], ["dependencies"])
        return [self.new_field, self.old_field, self.files_field, self.serializer_field, self.dataminer_field, self.dependencies_field]

    def create_final(self) -> DataminerSettings.DataminerSettings:
        return DataminerSettings.DataminerSettings(
            kwargs=self.arguments,
            domain=self.domain
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        parent = cast("DataminerCollectionComponent.DataminerCollectionComponent", self.get_inline_parent())
        exceptions.extend(self.final.link_subcomponents(
            file_name=parent.file_name,
            name=parent.name,
            structure=parent.structure_field.subcomponent.final,
            dataminer_class=self.dataminer_field.dataminer,
            serializers=self.serializer_field.final,
            dependencies=list(self.dependencies_field.map(lambda dataminer_collection_component: dataminer_collection_component.subcomponent.final)),
            start_version=self.old_field.final,
            end_version=self.new_field.final,
            version_file_types=list(self.files_field.map(lambda version_file_type_field: version_file_type_field.final))
        ))
        return exceptions

    def check(self) -> list[Exception]:
        exceptions = super().check()
        if self.dataminer_field.exists:
            if not self.files_field_exists:
                exceptions.append(Exceptions.DataminerCollectionFileError(False, self, "when \"name\" is not null"))
        else:
            if self.files_field_exists:
                exceptions.append(Exceptions.DataminerCollectionFileError(True, self, "when \"name\" is null"))
        return exceptions
