from typing import Any, Mapping

import Domain.Domain as Domain
from Component.ComponentObject import ComponentObject
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Utilities.TypeVerifier import TypedDictTypeVerifier
from Version.Version import Version


class VersionProviderCreator(ComponentObject):

    __slots__ = (
        "version_provider"
    )

    def link_version_provider_creator(self, version_provider_class:type["VersionProvider"], arguments:Mapping[str,Any]) -> None:
        self.version_provider = version_provider_class(self.full_name, self.domain, **arguments)

class VersionProvider():

    __slots__ = (
        "domain",
        "full_name",
    )

    type_verifier:TypedDictTypeVerifier = TypedDictTypeVerifier()

    def __init__(self, full_name:str, domain:"Domain.Domain") -> None:
        self.full_name = full_name
        self.domain = domain

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_name}>"

    def get_versions(self, versions:list[Version], *, supports_dataminer_collection:AbstractDataminerCollection|None=None) -> list[Version]:
        """
        :param versions: List of all versions from oldest to newest.
        :returns: Subset of versions that this VersionProvider is searching for, sorted oldest to newest.
        """
        ...
