import re

import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Dataminer.AbstractDataminerCollectionComponent as AbstractDataminerCollectionComponent
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Structure.BaseComponent as BaseComponent
import Dataminer.CoverageDataminer as CoverageDataminer
import Utilities.TypeVerifier as TypeVerifier


class CoverageDataminerCollectionComponent(AbstractDataminerCollectionComponent.AbstractDataminerCollectionComponent[CoverageDataminer.CoverageDataminer]):

    class_name = "CoverageDataminerCollection"
    my_capabilities = Capabilities.Capabilities(is_dataminer_collection=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("comparing_disabled", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("disabled", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("file_list_dataminer", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("file_name", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("remove_files", False, TypeVerifier.ListTypeVerifier(str, list)),
        TypeVerifier.TypedDictKeyTypeVerifier("remove_regex", False, TypeVerifier.ListTypeVerifier(str, list)),
        TypeVerifier.TypedDictKeyTypeVerifier("remove_prefixes", False, TypeVerifier.ListTypeVerifier(str, list)),
        TypeVerifier.TypedDictKeyTypeVerifier("remove_suffixes", False, TypeVerifier.ListTypeVerifier(str, list)),
        TypeVerifier.TypedDictKeyTypeVerifier("structure", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
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

        self.file_list_dataminer_field = ComponentField.ComponentField(data["file_list_dataminer"], AbstractDataminerCollectionComponent.ABSTRACT_DATAMINER_COLLECTION_PATTERN, ["file_list_dataminer"], allow_inline=Field.InlinePermissions.reference, assume_component_group="dataminer_collections")
        self.structure_field = ComponentField.ComponentField(data["structure"], BaseComponent.STRUCTURE_BASE_PATTERN, ["structure"], allow_inline=Field.InlinePermissions.reference)
        return [self.file_list_dataminer_field, self.structure_field]

    def create_final(self) -> CoverageDataminer.CoverageDataminer:
        return CoverageDataminer.CoverageDataminer(
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
        self.final.link_subcomponents(
            file_list_dataminer=self.file_list_dataminer_field.subcomponent.final,
            structure=self.structure_field.subcomponent.final,
        )
        return exceptions
