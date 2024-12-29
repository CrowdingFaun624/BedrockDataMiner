import re

import Component.ComponentTyping as ComponentTyping
import Component.Dataminer.AbstractDataminerCollectionComponent as AbstractDataminerCollectionComponent
import Component.Dataminer.Field.DataminerCollectionField as DataminerCollectionField
import Component.Field.Field as Field
import Component.Structure.Field.StructureField as StructureField
import Dataminer.CoverageDataminer as CoverageDataminer
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class CoverageDataminerCollectionComponent(AbstractDataminerCollectionComponent.AbstractDataminerCollectionComponent[CoverageDataminer.CoverageDataminer]):

    class_name_article = "a CoverageDataminerCollection"
    class_name = "CoverageDataminerCollection"
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

    def initialize_fields(self, data: ComponentTyping.CoverageDataminerCollectionTypedDict) -> list[Field.Field]:
        self.file_name = data["file_name"]
        self.comparing_disabled = data.get("comparing_disabled", False)
        self.disabled = data.get("disabled", False)
        self.remove_files = set(data.get("remove_files", []))
        self.remove_regex = [re.compile(pattern) for pattern in data.get("remove_regex", [])]
        self.remove_prefixes = data.get("remove_prefixes", [])
        self.remove_suffixes = data.get("remove_suffixes", [])

        self.file_list_dataminer_field = DataminerCollectionField.DataminerCollectionField(data["file_list_dataminer"], ["file_list_dataminer"])
        self.structure_field = StructureField.StructureField(data["structure"], ["structure"])
        return [self.file_list_dataminer_field, self.structure_field]

    def create_final(self) -> None:
        super().create_final()
        self.final = CoverageDataminer.CoverageDataminer(
            file_name=self.file_name,
            name=self.name,
            domain=self.domain,
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
