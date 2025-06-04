import re
from typing import Sequence

from Component.Capabilities import Capabilities
from Component.ComponentTyping import CoverageDataminerCollectionTypedDict
from Component.Dataminer.AbstractDataminerCollectionComponent import (
    ABSTRACT_DATAMINER_COLLECTION_PATTERN,
    AbstractDataminerCollectionComponent,
)
from Component.Field.ComponentField import ComponentField
from Component.Field.Field import Field, InlinePermissions
from Component.Structure.StructureBaseComponent import STRUCTURE_BASE_PATTERN
from Dataminer.CoverageDataminer import CoverageDataminer
from Structure.StructureInfo import StructureInfo
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class CoverageDataminerCollectionComponent(AbstractDataminerCollectionComponent[CoverageDataminer]):

    class_name = "CoverageDataminerCollection"
    my_capabilities = Capabilities(is_dataminer_collection=True)
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("comparing_disabled", False, bool),
        TypedDictKeyTypeVerifier("disabled", False, bool),
        TypedDictKeyTypeVerifier("file_list_dataminer", True, str),
        TypedDictKeyTypeVerifier("file_name", True, str),
        TypedDictKeyTypeVerifier("remove_files", False, ListTypeVerifier(str, list)),
        TypedDictKeyTypeVerifier("remove_regex", False, ListTypeVerifier(str, list)),
        TypedDictKeyTypeVerifier("remove_prefixes", False, ListTypeVerifier(str, list)),
        TypedDictKeyTypeVerifier("remove_suffixes", False, ListTypeVerifier(str, list)),
        TypedDictKeyTypeVerifier("structure", True, str),
        TypedDictKeyTypeVerifier("type", False, str),
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
        "structure_info",
    )

    def initialize_fields(self, data: CoverageDataminerCollectionTypedDict) -> Sequence[Field]:
        self.file_name = data["file_name"]
        self.comparing_disabled = data.get("comparing_disabled", False)
        self.disabled = data.get("disabled", False)
        self.remove_files = set(data.get("remove_files", ()))
        self.remove_regex = [re.compile(pattern) for pattern in data.get("remove_regex", ())]
        self.remove_prefixes = data.get("remove_prefixes", [])
        self.remove_suffixes = data.get("remove_suffixes", [])
        self.structure_info = data.get("structure_info", {})

        self.file_list_dataminer_field = ComponentField(data["file_list_dataminer"], ABSTRACT_DATAMINER_COLLECTION_PATTERN, ("file_list_dataminer",), allow_inline=InlinePermissions.reference, assume_component_group="dataminer_collections")
        self.structure_field = ComponentField(data["structure"], STRUCTURE_BASE_PATTERN, ("structure",), allow_inline=InlinePermissions.reference)
        return (self.file_list_dataminer_field, self.structure_field)

    def create_final(self, trace:Trace) -> CoverageDataminer:
        return CoverageDataminer(
            file_name=self.file_name,
            name=self.name,
            domain=self.domain,
            comparing_disabled=self.comparing_disabled,
            remove_files=self.remove_files,
            remove_regex=self.remove_regex,
            remove_prefixes=self.remove_prefixes,
            remove_suffixes=self.remove_suffixes,
        )

    def link_finals(self, trace:Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_subcomponents(
                file_list_dataminer=self.file_list_dataminer_field.subcomponent.final,
                structure=self.structure_field.subcomponent.final,
                structure_info=StructureInfo(self.structure_info, self.domain, repr(self))
            )
