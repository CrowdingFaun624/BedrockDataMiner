from typing import Sequence, cast

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Dataminer.AbstractDataminerCollectionComponent as AbstractDataminerCollectionComponent
import Component.Dataminer.DataminerCollectionComponent as DataminerCollectionComponent
import Component.Field.ComponentField as ComponentField
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.FieldListField as FieldListField
import Component.Field.ScriptedClassField as ScriptedClassField
import Component.Pattern as Pattern
import Component.Version.VersionComponent as VersionComponent
import Component.Version.VersionFileTypeComponent as VersionFileTypeComponent
import Dataminer.Dataminer as Dataminer
import Dataminer.DataminerSettings as DataminerSettings
import Structure.StructureInfo as StructureInfo
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

DATAMINER_SETTINGS_PATTERN:Pattern.Pattern["DataminerSettingsComponent"] = Pattern.Pattern("is_dataminer_settings")

class DataminerSettingsComponent(Component.Component[DataminerSettings.DataminerSettings]):

    class_name = "DataminerSettings"
    my_capabilities = Capabilities.Capabilities(is_dataminer_settings=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("dependencies", False, TypeVerifier.ListTypeVerifier(str, list)),
        TypeVerifier.TypedDictKeyTypeVerifier("files", False, TypeVerifier.ListTypeVerifier(str, list)),
        TypeVerifier.TypedDictKeyTypeVerifier("name", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("new", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("old", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("structure_info", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "arguments",
        "dataminer_field",
        "dependencies_field",
        "files_field",
        "files_field_exists",
        "new_field",
        "old_field",
        "structure_info",
    )

    def initialize_fields(self, data: ComponentTyping.DataminerSettingsTypedDict) -> Sequence[Field.Field]:
        self.files_field_exists = "files" in data
        self.arguments = data.get("arguments", {})
        self.structure_info = data.get("structure_info", {})

        self.new_field = ComponentField.OptionalComponentField(data["new"], VersionComponent.VERSION_PATTERN, ("new",), assume_component_group="versions")
        self.old_field = ComponentField.OptionalComponentField(data["old"], VersionComponent.VERSION_PATTERN, ("old",), assume_component_group="versions")
        self.files_field = ComponentListField.ComponentListField(data.get("files", ()), VersionFileTypeComponent.VERSION_FILE_TYPE_PATTERN, ("files",), allow_inline=Field.InlinePermissions.reference, assume_component_group="version_file_types")
        self.dataminer_field = ScriptedClassField.OptionalScriptedClassField(data["name"], lambda script_set_set_set: script_set_set_set.dataminer_classes, ("name",), default=Dataminer.NullDataminer)
        self.dependencies_field = FieldListField.FieldListField([
            ComponentField.ComponentField(
                dependency_name,
                AbstractDataminerCollectionComponent.ABSTRACT_DATAMINER_COLLECTION_PATTERN,
                ("dependencies", str(index)),
                allow_inline=Field.InlinePermissions.reference
            ) for index, dependency_name in enumerate(data.get("dependencies", ()))
        ], ("dependencies",))
        return (self.new_field, self.old_field, self.files_field, self.dataminer_field, self.dependencies_field)

    def create_final(self, trace:Trace.Trace) -> DataminerSettings.DataminerSettings:
        return DataminerSettings.DataminerSettings(
            kwargs=self.arguments,
            domain=self.domain
        )

    def link_finals(self, trace:Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            parent = cast("DataminerCollectionComponent.DataminerCollectionComponent", self.get_inline_parent())
            self.final.link_subcomponents(
                trace,
                file_name=parent.file_name,
                name=parent.name,
                structure=parent.structure_field.subcomponent.final,
                dataminer_class=self.dataminer_field.object_class,
                dependencies=list(self.dependencies_field.map(lambda dataminer_collection_component: dataminer_collection_component.subcomponent.final)),
                start_version=self.old_field.map(lambda subcomponent: subcomponent.final),
                end_version=self.new_field.map(lambda subcomponent: subcomponent.final),
                structure_info=StructureInfo.StructureInfo(self.structure_info, self.domain, repr(self)),
                version_file_types=list(self.files_field.map(lambda version_file_type_field: version_file_type_field.final))
            )

    def check(self, trace:Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().check(trace)
            if self.dataminer_field.exists:
                if not self.files_field_exists:
                    trace.exception(Exceptions.DataminerCollectionFileError(False, "when \"name\" is not null"))
            else:
                if self.files_field_exists:
                    trace.exception(Exceptions.DataminerCollectionFileError(True, "when \"name\" is null"))
