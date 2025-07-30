from typing import TYPE_CHECKING, Sequence, cast

from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import DataminerSettingsTypedDict
from Component.Dataminer.AbstractDataminerCollectionComponent import (
    ABSTRACT_DATAMINER_COLLECTION_PATTERN,
)
from Component.Field.ComponentField import ComponentField, OptionalComponentField
from Component.Field.ComponentListField import ComponentListField
from Component.Field.Field import Field
from Component.Field.FieldListField import FieldListField
from Component.Field.ScriptedClassField import OptionalScriptedClassField
from Component.Pattern import Pattern
from Component.Permissions import InlinePermissions
from Component.Version.VersionComponent import VERSION_PATTERN
from Component.Version.VersionFileTypeComponent import VERSION_FILE_TYPE_PATTERN
from Dataminer.Dataminer import NullDataminer
from Dataminer.DataminerSettings import DataminerSettings
from Structure.StructureInfo import StructureInfo
from Utilities.Exceptions import DataminerCollectionFileError
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)

if TYPE_CHECKING:
    from Component.Dataminer.DataminerCollectionComponent import (
        DataminerCollectionComponent,
    )

DATAMINER_SETTINGS_PATTERN:Pattern["DataminerSettingsComponent"] = Pattern("is_dataminer_settings")

class DataminerSettingsComponent(Component[DataminerSettings]):

    class_name = "DataminerSettings"
    my_capabilities = Capabilities(is_dataminer_settings=True)
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("arguments", False, dict),
        TypedDictKeyTypeVerifier("dependencies", False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("files", False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("name", True, (str, type(None))),
        TypedDictKeyTypeVerifier("new", True, (str, type(None))),
        TypedDictKeyTypeVerifier("old", True, (str, type(None))),
        TypedDictKeyTypeVerifier("optional_dependencies", False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("structure_info", False, dict),
        TypedDictKeyTypeVerifier("type", False, str),
    )
    inline_permissions = InlinePermissions.inline

    __slots__ = (
        "arguments",
        "dataminer_field",
        "dependencies_field",
        "files_field",
        "files_field_exists",
        "new_field",
        "old_field",
        "optional_dependencies_field",
        "structure_info",
    )

    def initialize_fields(self, data: DataminerSettingsTypedDict) -> Sequence[Field]:
        self.files_field_exists = "files" in data
        self.arguments = data.get("arguments", {})
        self.structure_info = data.get("structure_info", {})

        self.new_field = OptionalComponentField(data["new"], VERSION_PATTERN, ("new",))
        self.old_field = OptionalComponentField(data["old"], VERSION_PATTERN, ("old",))
        self.files_field = ComponentListField(data.get("files", ()), VERSION_FILE_TYPE_PATTERN, ("files",))
        self.dataminer_field = OptionalScriptedClassField(data["name"], lambda script_set_set_set: script_set_set_set.dataminer_classes, ("name",), default=NullDataminer)
        self.dependencies_field = ComponentListField(data.get("dependencies", ()), ABSTRACT_DATAMINER_COLLECTION_PATTERN, ("dependencies",))
        self.optional_dependencies_field = ComponentListField(data.get("optional_dependencies", ()), ABSTRACT_DATAMINER_COLLECTION_PATTERN, ("optional_dependencies",))
        return (self.new_field, self.old_field, self.files_field, self.dataminer_field, self.dependencies_field, self.optional_dependencies_field)

    def create_final(self, trace:Trace) -> DataminerSettings:
        return DataminerSettings(
            full_name=self.full_name,
            kwargs=self.arguments,
            domain=self.domain
        )

    def link_finals(self, trace:Trace) -> None:
        parent = cast("DataminerCollectionComponent", self.get_inline_parent())
        self.final.link_subcomponents(
            trace,
            file_name=parent.file_name,
            name=parent.name,
            structure=parent.structure_field.subcomponent.final,
            dataminer_class=self.dataminer_field.object_class,
            dependencies=list(self.dependencies_field.map(lambda dataminer_collection_component: dataminer_collection_component.final)),
            optional_dependencies=list(self.optional_dependencies_field.map(lambda dataminer_collection_component: dataminer_collection_component.final)),
            start_version=self.old_field.map(lambda subcomponent: subcomponent.final),
            end_version=self.new_field.map(lambda subcomponent: subcomponent.final),
            structure_info=StructureInfo(self.structure_info, self.domain, repr(self)),
            version_file_types=list(self.files_field.map(lambda version_file_type_field: version_file_type_field.final))
        )

    def check(self, trace:Trace) -> None:
        if self.dataminer_field.exists:
            if not self.files_field_exists:
                trace.exception(DataminerCollectionFileError(False, "when \"name\" is not null"))
        else:
            if self.files_field_exists:
                trace.exception(DataminerCollectionFileError(True, "when \"name\" is null"))
