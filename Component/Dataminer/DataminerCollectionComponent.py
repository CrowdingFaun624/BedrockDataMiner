from itertools import batched
from typing import Sequence

import Component.ComponentTyping as ComponentTyping
import Component.Dataminer.AbstractDataminerCollectionComponent as AbstractDataminerCollectionComponent
import Component.Dataminer.DataminerSettingsComponent as DataminerSettingsComponent
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Field.FieldListField as FieldListField
import Component.Structure.StructureBaseComponent as StructureBaseComponent
import Dataminer.DataminerCollection as DataminerCollection
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier
import Version.Version as Version


class DataminerCollectionComponent(AbstractDataminerCollectionComponent.AbstractDataminerCollectionComponent[DataminerCollection.DataminerCollection]):

    __slots__ = (
        "comparing_disabled",
        "dataminer_settings_field",
        "disabled",
        "file_name",
        "structure_field",
    )

    class_name = "DataminerCollection"
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("comparing_disabled", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("dataminers", True, TypeVerifier.ListTypeVerifier(dict, list)),
        TypeVerifier.TypedDictKeyTypeVerifier("disabled", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("file_name", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("structure", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
    )

    def initialize_fields(self, data: ComponentTyping.DataminerCollectionTypedDict) -> Sequence[Field.Field]:
        self.file_name = data["file_name"]
        self.comparing_disabled = data.get("comparing_disabled", False)
        self.disabled = data.get("disabled", False)

        self.structure_field = ComponentField.ComponentField(data["structure"], StructureBaseComponent.STRUCTURE_BASE_PATTERN, ("structure",), allow_inline=Field.InlinePermissions.reference)
        self.dataminer_settings_field = FieldListField.FieldListField([
            ComponentField.ComponentField(
                dataminer_settings_data,
                DataminerSettingsComponent.DATAMINER_SETTINGS_PATTERN,
                ("dataminers", str(index)),
                allow_inline=Field.InlinePermissions.inline,
                assume_type=DataminerSettingsComponent.DataminerSettingsComponent.class_name,
            ) for index, dataminer_settings_data in enumerate(data["dataminers"])
        ], ("dataminers",))
        return (self.structure_field, self.dataminer_settings_field)

    def create_final(self, trace:Trace.Trace) -> DataminerCollection.DataminerCollection:
        return DataminerCollection.DataminerCollection(
            file_name=self.file_name,
            name=self.name,
            domain=self.domain,
            comparing_disabled=self.comparing_disabled,
        )

    def link_finals(self, trace:Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_subcomponents(
                structure=self.structure_field.subcomponent.final,
                dataminer_settings=list(self.dataminer_settings_field.map(lambda dataminer_settings_field: dataminer_settings_field.subcomponent.final))
            )

    def check(self, trace:Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().check(trace)
            dataminer_settings_components = self.dataminer_settings_field.map(lambda dataminer_settings_field: dataminer_settings_field.subcomponent)

            # ending DataminerSettings must have null versions on corresponding versions; middle ones cannot be null.
            used_versions:list[Version.Version] = []
            for index, dataminer_settings_component in enumerate(dataminer_settings_components):
                with trace.enter_key(index, dataminer_settings_component):
                    new_version = dataminer_settings_component.new_field.map(lambda subcomponent: subcomponent.final)
                    old_version = dataminer_settings_component.old_field.map(lambda subcomponent: subcomponent.final)
                    if index == 0:
                        if new_version is not None:
                            trace.exception(Exceptions.ComponentVersionRangeExists(new_version, True))
                            continue
                    else:
                        if new_version is None:
                            trace.exception(Exceptions.ComponentVersionRangeMissing("new"))
                            continue
                        used_versions.append(new_version)
                    if index == len(self.dataminer_settings_field) - 1:
                        if old_version is not None:
                            trace.exception(Exceptions.ComponentVersionRangeExists(old_version, False))
                            continue
                    else:
                        if old_version is None:
                            trace.exception(Exceptions.ComponentVersionRangeMissing("old"))
                            continue
                        used_versions.append(old_version)

            for new_version, old_version in batched(used_versions, 2, strict=True):
                if new_version != old_version:
                    trace.exception(Exceptions.ComponentVersionRangeGap(new_version, old_version))
