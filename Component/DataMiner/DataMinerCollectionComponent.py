from itertools import batched

import Component.ComponentTyping as ComponentTyping
import Component.Dataminer.AbstractDataminerCollectionComponent as AbstractDataminerCollectionComponent
import Component.Dataminer.DataminerSettingsComponent as DataminerSettingsComponent
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Field.FieldListField as FieldListField
import Component.Pattern as Pattern
import Component.Structure.Field.StructureField as StructureField
import Dataminer.DataminerCollection as DataminerCollection
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Version.Version as Version

DATAMINER_SETTINGS_PATTERN:Pattern.Pattern[DataminerSettingsComponent.DataminerSettingsComponent] = Pattern.Pattern([{"is_dataminer_settings": True}])

class DataminerCollectionComponent(AbstractDataminerCollectionComponent.AbstractDataminerCollectionComponent[DataminerCollection.DataminerCollection]):

    __slots__ = (
        "comparing_disabled",
        "dataminer_settings_field",
        "disabled",
        "file_name",
        "structure_field",
    )

    class_name_article = "a DataminerCollection"
    class_name = "DataminerCollection"
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("comparing_disabled", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("dataminers", "a list", True, TypeVerifier.ListTypeVerifier(dict, list, "a dict", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("disabled", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("file_name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("structure", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    def initialize_fields(self, data: ComponentTyping.DataminerCollectionTypedDict) -> list[Field.Field]:
        self.file_name = data["file_name"]
        self.comparing_disabled = data.get("comparing_disabled", False)
        self.disabled = data.get("disabled", False)

        self.structure_field = StructureField.StructureField(data["structure"], ["structure"])
        self.dataminer_settings_field = FieldListField.FieldListField([
            ComponentField.ComponentField(
                dataminer_settings_data,
                DATAMINER_SETTINGS_PATTERN,
                ["dataminers", index],
                allow_inline=Field.InlinePermissions.inline,
                assume_type=DataminerSettingsComponent.DataminerSettingsComponent.class_name
            ) for index, dataminer_settings_data in enumerate(data["dataminers"])
        ], ["dataminers"])
        return [self.structure_field, self.dataminer_settings_field]

    def create_final(self) -> None:
        super().create_final()
        self.final = DataminerCollection.DataminerCollection(
            file_name=self.file_name,
            name=self.name,
            domain=self.domain,
            comparing_disabled=self.comparing_disabled,
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.get_final().link_subcomponents(
            structure=self.structure_field.get_final(),
            dataminer_settings=list(self.dataminer_settings_field.map(lambda dataminer_settings_field: dataminer_settings_field.get_component().get_final()))
        )
        return exceptions

    def check(self) -> list[Exception]:
        exceptions = super().check()
        dataminer_settings_components = self.dataminer_settings_field.map(lambda dataminer_settings_field: dataminer_settings_field.get_component())

        # ending DataminerSettings must have null versions on corresponding versions; middle ones cannot be null.
        used_versions:list[Version.Version] = []
        for index, dataminer_settings_component in enumerate(dataminer_settings_components):
            new_version = dataminer_settings_component.new_field.get_final()
            old_version = dataminer_settings_component.old_field.get_final()
            if index == 0:
                if new_version is not None:
                    exceptions.append(Exceptions.ComponentVersionRangeExists(self, new_version, True))
                    continue
            else:
                if new_version is None:
                    exceptions.append(Exceptions.ComponentVersionRangeMissing(self, index, "new"))
                    continue
                used_versions.append(new_version)
            if index == len(self.dataminer_settings_field) - 1:
                if old_version is not None:
                    exceptions.append(Exceptions.ComponentVersionRangeExists(self, old_version, False))
                    continue
            else:
                if old_version is None:
                    exceptions.append(Exceptions.ComponentVersionRangeMissing(self, index, "old"))
                    continue
                used_versions.append(old_version)

        for new_version, old_version in batched(used_versions, 2, strict=True):
            if new_version != old_version:
                exceptions.append(Exceptions.ComponentVersionRangeGap(self, new_version, old_version))

        return exceptions
