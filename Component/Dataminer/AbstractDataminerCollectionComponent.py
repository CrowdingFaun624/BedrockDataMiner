from typing import NotRequired, Required, TypedDict

from Component.Component import Component
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Structure.StructureBase import StructureBase
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class AbstractDataminerCollectionTypedDict(TypedDict):
    comparing_disabled: NotRequired[bool]
    file_name: Required[str]
    structure: Required[StructureBase]

class AbstractDataminerCollectionComponent[R: AbstractDataminerCollection, P: AbstractDataminerCollectionTypedDict](Component[R, P]):

    type_name = "AbstractDataminerCollection"
    object_type = AbstractDataminerCollection
    abstract = True

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("comparing_disabled", False, bool),
        TypedDictKeyTypeVerifier("file_name", True, str),
        TypedDictKeyTypeVerifier("structure", True, StructureBase),
    ))

    def link_final(self, fields: P) -> None:
        super().link_final(fields)
        self.final.link_abstract_dataminer_collection(
            comparing_disabled=fields.get("comparing_disabled", False),
            file_name=fields["file_name"],
            structure=fields["structure"]
        )
