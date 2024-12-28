import re

import Component.ComponentTyping as ComponentTyping
import Component.DataMiner.AbstractDataMinerCollectionComponent as AbstractDataMinerCollectionComponent
import Component.DataMiner.Field.DataMinerCollectionField as DataMinerCollectionField
import Component.Structure.Field.StructureField as StructureField
import DataMiner.CoverageDataMiner as CoverageDataMiner
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class CoverageDataMinerCollectionComponent(AbstractDataMinerCollectionComponent.AbstractDataMinerCollectionComponent[CoverageDataMiner.CoverageDataMiner]):

    class_name_article = "a CoverageDataMinerCollection"
    class_name = "CoverageDataMinerCollection"
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("comparing_disabled", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("disabled", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("file_list_dataminer", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("file_name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("remove_files", "a list of str", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("remove_regex", "a list of str", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("remove_prefixes", "a list of str", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("remove_suffixes", "a list of str", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("structure", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    __slots__ = (
        "comparing_disabled",
        "disabled",
        "file_list_dataminer_field",
        "file_name",
        "remove_files",
        "remove_prefixes",
        "remove_regex",
        "remove_suffixes",
        "structure_field",
    )

    def __init__(self, data: ComponentTyping.CoverageDataMinerCollectionTypedDict, name: str, component_group: str, index: int | None) -> None:
        super().__init__(data, name, component_group, index)

        self.file_name = data["file_name"]
        self.comparing_disabled = data.get("comparing_disabled", False)
        self.disabled = data.get("disabled", False)
        self.remove_files = set(data.get("remove_files", []))
        self.remove_regex = [re.compile(pattern) for pattern in data.get("remove_regex", [])]
        self.remove_prefixes = data.get("remove_prefixes", [])
        self.remove_suffixes = data.get("remove_suffixes", [])

        self.file_list_dataminer_field = DataMinerCollectionField.DataMinerCollectionField(data["file_list_dataminer"], ["file_list_dataminer"])
        self.structure_field = StructureField.StructureField(data["structure"], ["structure"])
        self.fields.extend([self.file_list_dataminer_field, self.structure_field])

    def create_final(self) -> None:
        super().create_final()
        self.final = CoverageDataMiner.CoverageDataMiner(
            file_name=self.file_name,
            name=self.name,
            comparing_disabled=self.comparing_disabled,
            remove_files=self.remove_files,
            remove_regex=self.remove_regex,
            remove_prefixes=self.remove_prefixes,
            remove_suffixes=self.remove_suffixes,
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.get_final().link_subcomponents(
            file_list_dataminer=self.file_list_dataminer_field.get_final(),
            structure=self.structure_field.get_final(),
        )
        return exceptions
