import DataMiner.AbstractDataMinerCollection as AbstractDataMinerCollection
import Domain.Domain as Domain
import Version.Version as Version


class VersionProvider():

    def __init__(self, domain:"Domain.Domain") -> None:
        self.domain = domain

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def get_versions(self, versions:list[Version.Version], *, supports_dataminer_collection:AbstractDataMinerCollection.AbstractDataMinerCollection|None=None) -> list[Version.Version]:
        '''
        :versions: List of all versions from oldest to newest.
        :return: Subset of versions that this VersionProvider is searching for, sorted oldest to newest.
        '''
        ...
