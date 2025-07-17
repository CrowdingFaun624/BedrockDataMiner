from itertools import batched
from typing import Sequence

import Utilities.Exceptions as Exceptions
from Component.ComponentTyping import DataminerCollectionTypedDict
from Component.Dataminer.AbstractDataminerCollectionComponent import (
    AbstractDataminerCollectionComponent,
)
from Component.Dataminer.DataminerSettingsComponent import (
    DATAMINER_SETTINGS_PATTERN,
    DataminerSettingsComponent,
)
from Component.Field.ComponentField import ComponentField
from Component.Field.Field import Field, InlinePermissions
from Component.Field.FieldListField import FieldListField
from Component.Structure.StructureBaseComponent import STRUCTURE_BASE_PATTERN
from Dataminer.DataminerCollection import DataminerCollection
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)
from Version.Version import Version


class DataminerCollectionComponent(AbstractDataminerCollectionComponent[DataminerCollection]):

    __slots__ = (
        "comparing_disabled",
        "dataminer_settings_field",
        "disabled",
        "file_name",
        "structure_field",
    )

    class_name = "DataminerCollection"
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("comparing_disabled", False, bool),
        TypedDictKeyTypeVerifier("dataminers", True, ListTypeVerifier(dict, list)),
        TypedDictKeyTypeVerifier("disabled", False, bool),
        TypedDictKeyTypeVerifier("file_name", True, str),
        TypedDictKeyTypeVerifier("structure", True, (str, dict)),
        TypedDictKeyTypeVerifier("type", False, str),
    )

    def initialize_fields(self, data: DataminerCollectionTypedDict) -> Sequence[Field]:
        self.file_name = data["file_name"]
        self.comparing_disabled = data.get("comparing_disabled", False)
        self.disabled = data.get("disabled", False)

        self.structure_field = ComponentField(data["structure"], STRUCTURE_BASE_PATTERN, ("structure",), allow_inline=InlinePermissions.reference)
        self.dataminer_settings_field = FieldListField([
            ComponentField(
                dataminer_settings_data,
                DATAMINER_SETTINGS_PATTERN,
                (str(index),),
                ("dataminers", str(index)),
                allow_inline=InlinePermissions.inline,
                assume_type=DataminerSettingsComponent.class_name,
            ) for index, dataminer_settings_data in enumerate(data["dataminers"])
        ], ("dataminers",))
        return (self.structure_field, self.dataminer_settings_field)

    def create_final(self, trace:Trace) -> DataminerCollection:
        return DataminerCollection(
            file_name=self.file_name,
            name=self.name,
            full_name=self.full_name,
            domain=self.domain,
            comparing_disabled=self.comparing_disabled,
        )

    def link_finals(self, trace:Trace) -> None:
        self.final.link_subcomponents(
            structure=self.structure_field.subcomponent.final,
            dataminer_settings=list(self.dataminer_settings_field.map(lambda dataminer_settings_field: dataminer_settings_field.subcomponent.final))
        )

    def check(self, trace:Trace) -> None:
        dataminer_settings_components = self.dataminer_settings_field.map(lambda dataminer_settings_field: dataminer_settings_field.subcomponent)

        # ending DataminerSettings must have null versions on corresponding versions; middle ones cannot be null.
        used_versions:list[Version] = []
        error_exists:bool = False # used to prevent `batched` from giving a separate error
        for index, dataminer_settings_component in enumerate(dataminer_settings_components):
            with trace.enter_key(index, dataminer_settings_component):
                new_version = dataminer_settings_component.new_field.map(lambda subcomponent: subcomponent.final)
                old_version = dataminer_settings_component.old_field.map(lambda subcomponent: subcomponent.final)
                if index == 0:
                    if new_version is not None:
                        error_exists = True
                        trace.exception(Exceptions.ComponentVersionRangeExists(new_version, True))
                        continue
                else:
                    if new_version is None:
                        error_exists = True
                        trace.exception(Exceptions.ComponentVersionRangeMissing("new"))
                        continue
                    used_versions.append(new_version)
                if index == len(self.dataminer_settings_field) - 1:
                    if old_version is not None:
                        error_exists = True
                        trace.exception(Exceptions.ComponentVersionRangeExists(old_version, False))
                        continue
                else:
                    if old_version is None:
                        error_exists = True
                        trace.exception(Exceptions.ComponentVersionRangeMissing("old"))
                        continue
                    used_versions.append(old_version)

        if not error_exists:
            for new_version, old_version in batched(used_versions, 2, strict=True):
                if new_version != old_version:
                    trace.exception(Exceptions.ComponentVersionRangeGap(new_version, old_version))
