from typing import Required, TypedDict

from Component.Component import Component
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Structure.StructureBase import StructureBase
from Tablifier.Tablifier import Tablifier
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier
from Version.VersionProvider.VersionProvider import VersionProviderCreator


class TablifierTypedDict(TypedDict):
    dataminer_collection: Required[AbstractDataminerCollection]
    file_name: Required[str]
    structure: Required[StructureBase]
    version_provider: Required[VersionProviderCreator]

class TablifierComponent(Component[Tablifier, TablifierTypedDict]):

    type_name = "Tablifier"
    object_type = Tablifier
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("dataminer_collection", True, AbstractDataminerCollection),
        TypedDictKeyTypeVerifier("file_name", True, str),
        TypedDictKeyTypeVerifier("structure", True, StructureBase),
        TypedDictKeyTypeVerifier("version_provider", True, VersionProviderCreator),
    ))

    def link_final(self, fields: TablifierTypedDict) -> None:
        super().link_final(fields)
        self.final.link_tablifier(
            dataminer_collection=fields["dataminer_collection"],
            file_name=fields["file_name"],
            structure=fields["structure"],
            version_provider=fields["version_provider"],
        )
