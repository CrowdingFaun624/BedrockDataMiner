import Domain.Domain as Domain
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Version.Version import Version


class VersionProvider():

    __slots__ = (
        "domain",
    )

    def __init__(self, domain:"Domain.Domain") -> None:
        self.domain = domain

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def get_versions(self, versions:list[Version], *, supports_dataminer_collection:AbstractDataminerCollection|None=None) -> list[Version]:
        '''
        :versions: List of all versions from oldest to newest.
        :return: Subset of versions that this VersionProvider is searching for, sorted oldest to newest.
        '''
        ...
