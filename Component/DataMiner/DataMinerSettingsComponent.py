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
import Component.Version.Field.OptionalVersionField as OptionalVersionField
import DataMiner.DataMinerSettings as DataMinerSettings
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

if TYPE_CHECKING:
    import Component.DataMiner.DataMinerCollectionComponent as DataMinerCollectionComponent
    import Component.Version.VersionFileTypeComponent as VersionFileTypeComponent

DEPENDENCY_PATTERN:Pattern.Pattern["DataMinerCollectionComponent.DataMinerCollectionComponent"] = Pattern.Pattern([{"is_dataminer_collection": True}])
VERSION_FILE_TYPE_PATTERN:Pattern.Pattern["VersionFileTypeComponent.VersionFileTypeComponent"] = Pattern.Pattern([{"is_version_file_type": True}])

class DataMinerSettingsComponent(Component.Component[DataMinerSettings.DataMinerSettings]):

    class_name_article = "a DataMinerSettings"
    class_name = "DataMinerSettings"
    my_capabilities = Capabilities.Capabilities(is_dataminer_settings=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("new", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("old", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("files", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("dependencies", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("parameters", "a dict", False, dict),
    )

    def __init__(self, data:ComponentTyping.DataMinerSettingsComponentTypedDict, name: str, component_group: str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data, name)

        self.files_field_exists = "files" in data
        self.parameters = data.get("parameters", {})

        self.new_field = OptionalVersionField.OptionalVersionField(data["new"], ["new"])
        self.old_field = OptionalVersionField.OptionalVersionField(data["old"], ["old"])
        self.files_field = ComponentListField.ComponentListField(data.get("files", []), VERSION_FILE_TYPE_PATTERN, ["files"], allow_inline=Field.InLinePermissions.reference)
        self.dataminer_field = OptionalDataMinerTypeField.OptionalDataMinerTypeField(data["name"], ["name"])
        self.dependencies_field = FieldListField.FieldListField([
            ComponentField.ComponentField(
                dependency_name,
                DEPENDENCY_PATTERN,
                ["dependencies", index],
                allow_inline=Field.InLinePermissions.reference
            ) for index, dependency_name in enumerate(data.get("dependencies", []))
        ], ["dependencies"])
        self.fields.extend([self.new_field, self.old_field, self.files_field, self.dataminer_field, self.dependencies_field])

    def create_final(self) -> None:
        super().create_final()
        self.final = DataMinerSettings.DataMinerSettings(
            kwargs=self.parameters
        )

    def link_finals(self) -> None:
        super().link_finals()
        parent = cast("DataMinerCollectionComponent.DataMinerCollectionComponent", self.get_inline_parent())
        self.get_final().link_subcomponents(
            file_name=parent.file_name,
            name=parent.name,
            structure=parent.structure_field.get_final(),
            dataminer_class=self.dataminer_field.get_final(),
            dependencies=list(self.dependencies_field.map(lambda dataminer_collection_component: dataminer_collection_component.get_component().get_final())),
            start_version=self.old_field.get_final(),
            end_version=self.new_field.get_final(),
            version_file_types=list(self.files_field.map(lambda version_file_type_field: version_file_type_field.get_final()))
        )

    def check(self) -> list[Exception]:
        exceptions = super().check()
        if self.dataminer_field.exists():
            if not self.files_field_exists:
                exceptions.append(Exceptions.DataMinerCollectionFileError(False, self, "when \"name\" is not null"))
        else:
            if self.files_field_exists:
                exceptions.append(Exceptions.DataMinerCollectionFileError(True, self, "when \"name\" is null"))
        dataminer_class = self.dataminer_field.get_final()
        parameters = dataminer_class.parameters
        if parameters is not None:
            type_verifier_trace = TypeVerifier.make_trace([self, dataminer_class.__name__])
            exceptions.extend(parameters.verify(self.parameters, type_verifier_trace))
        return exceptions
