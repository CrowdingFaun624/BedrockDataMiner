from typing import Generator, TypeVar

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.DataMiner.DataMinerSettingsComponent as DataMinerSettingsComponent
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Field.FieldListField as FieldListField
import Component.Pattern as Pattern
import Component.Structure.Field.StructureField as StructureField
import DataMiner.DataMinerCollection as DataMinerCollection
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Version.Version as Version

DATAMINER_SETTINGS_PATTERN:Pattern.Pattern[DataMinerSettingsComponent.DataMinerSettingsComponent] = Pattern.Pattern([{"is_dataminer_settings": True}])

a = TypeVar("a")
def glue_adjacent(iter:list[a]) -> Generator[tuple[a, a], None, None]:
    if len(iter) == 0: return
    for i in range(0, len(iter) - 1, 2):
        yield iter[i], iter[i + 1]

class DataMinerCollectionComponent(Component.Component[DataMinerCollection.DataMinerCollection]):

    class_name_article = "a DataMinerCollection"
    class_name = "DataMinerCollection"
    my_capabilities = Capabilities.Capabilities(is_dataminer_collection=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("file_name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("structure", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("disabled", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("dataminers", "a list", True, TypeVerifier.ListTypeVerifier(dict, list, "a dict", "a list"))
    )

    def __init__(self, data: ComponentTyping.DataMinerCollectionComponentTypedDict, name: str, component_group: str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data, name)

        self.file_name = data["file_name"]
        self.disabled = data.get("disabled", False)

        self.structure_field = StructureField.StructureField(data["structure"], ["structure"])
        self.dataminer_settings_field = FieldListField.FieldListField([
            ComponentField.ComponentField(
                dataminer_settings_data,
                DATAMINER_SETTINGS_PATTERN,
                ["dataminers", index],
                allow_inline=Field.InLinePermissions.inline,
                assume_type=DataMinerSettingsComponent.DataMinerSettingsComponent.class_name
            ) for index, dataminer_settings_data in enumerate(data["dataminers"])
        ], ["dataminers"])
        self.fields.extend([self.structure_field, self.dataminer_settings_field])

    def create_final(self) -> None:
        super().create_final()
        self.final = DataMinerCollection.DataMinerCollection(
            file_name=self.file_name,
            name=self.name,
        )

    def link_finals(self) -> None:
        super().link_finals()
        self.get_final().link_subcomponents(
            structure=self.structure_field.get_final(),
            dataminer_settings=list(self.dataminer_settings_field.map(lambda dataminer_settings_field: dataminer_settings_field.get_component().get_final()))
        )

    def check(self) -> list[Exception]:
        exceptions = super().check()
        dataminer_settings_components = list(self.dataminer_settings_field.map(lambda dataminer_settings_field: dataminer_settings_field.get_component()))

        # ending DataMinerSettings must have null versions on corresponding versions; middle ones cannot be null.
        used_versions:list[Version.Version] = []
        for index, dataminer_settings_component in enumerate(dataminer_settings_components):
            new_version = dataminer_settings_component.new_field.get_final()
            old_version = dataminer_settings_component.old_field.get_final()
            if index == 0:
                if new_version is not None:
                    exceptions.append(Exceptions.DataMinerSettingsVersionRangeExists(self, new_version, True))
                    continue
            else:
                if new_version is None:
                    exceptions.append(Exceptions.DataMinerSettingsVersionRangeMissing(self, index, "new"))
                    continue
                used_versions.append(new_version)
            if index == len(dataminer_settings_components) - 1:
                if old_version is not None:
                    exceptions.append(Exceptions.DataMinerSettingsVersionRangeExists(self, old_version, False))
                    continue
            else:
                if old_version is None:
                    exceptions.append(Exceptions.DataMinerSettingsVersionRangeMissing(self, index, "old"))
                    continue
                used_versions.append(old_version)

        for new_version, old_version in glue_adjacent(used_versions):
            if new_version != old_version:
                exceptions.append(Exceptions.DataMinerSettingsVersionRangeGap(self, new_version, old_version))

        return exceptions
