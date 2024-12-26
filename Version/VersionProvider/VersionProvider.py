import DataMiner.AbstractDataMinerCollection as AbstractDataMinerCollection
import Version.Version as Version


class VersionProvider():

    def get_versions(self, versions:list[Version.Version], *, supports_dataminer_collection:AbstractDataMinerCollection.AbstractDataMinerCollection|None=None) -> list[Version.Version]:
        '''
        :versions: List of all versions from oldest to newest.
        :return: Subset of versions that this VersionProvider is searching for, sorted oldest to newest.
        '''
        ...
