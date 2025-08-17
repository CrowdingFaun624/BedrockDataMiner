from typing import AbstractSet, Any, Mapping, NotRequired, Required, Sequence

from Component.Dataminer.AbstractDataminerCollectionComponent import (
    AbstractDataminerCollectionComponent,
    AbstractDataminerCollectionTypedDict,
)
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Dataminer.CoverageDataminer import CoverageDataminer
from Structure.StructureInfo import StructureInfo
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)
from Version.VersionFileType import VersionFileType


class CoverageDataminerCollectionComponentTypedDict(AbstractDataminerCollectionTypedDict):
    file: Required[VersionFileType]
    file_list_dataminer: Required[AbstractDataminerCollection]
    remove_files: NotRequired[str | Sequence[str]]
    remove_prefixes: NotRequired[str | Sequence[str]]
    remove_regex: NotRequired[str | Sequence[str]]
    remove_suffixes: NotRequired[str | Sequence[str]]
    structure_info: NotRequired[Mapping[str, Any]]

class CoverageDataminerCollectionComponent(AbstractDataminerCollectionComponent[CoverageDataminer, CoverageDataminerCollectionComponentTypedDict]):

    type_name = "CoverageDataminerCollection"
    object_type = CoverageDataminer
    abstract = False

    type_verifier = AbstractDataminerCollectionComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("file", True, VersionFileType),
        TypedDictKeyTypeVerifier("file_list_dataminer", True, AbstractDataminerCollection),
        TypedDictKeyTypeVerifier("remove_files",    False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("remove_prefixes", False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("remove_regex",    False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("remove_suffixes", False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("structure_info", False, DictTypeVerifier(dict, str, object))
    ))

    def link_final(self, fields: CoverageDataminerCollectionComponentTypedDict) -> None:
        super().link_final(fields)
        self.final.link_coverage_dataminer_collection(
            file=fields["file"],
            file_list_dataminer=fields["file_list_dataminer"],
            remove_files=fields.get("remove_files", []),
            remove_prefixes=fields.get("remove_prefixes", []),
            remove_regex=fields.get("remove_regex", []),
            remove_suffixes=fields.get("remove_suffixes", []),
            structure_info=StructureInfo(fields.get("structure_info", {}), self.group.domain, self.full_name),
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        if super().finalize(propagating_booleans, propagating_sets, trace):
            return True
        self.final.finalize_coverage_dataminer()
        return False
