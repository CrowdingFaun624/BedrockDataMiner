from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Version.Version import Version
from Version.VersionProvider.VersionProvider import VersionProvider


class LatestVersionProvider(VersionProvider):

    def get_most_recent_version(self, all_versions:list[Version], index:int, supports_dataminer_collection:AbstractDataminerCollection) -> Version|None:
        for i in range(index, -1, -1):
            version = all_versions[i]
            if supports_dataminer_collection.supports_version(version):
                return version
        else:
            return None

    def get_versions(self, versions: list[Version], *, supports_dataminer_collection:AbstractDataminerCollection) -> list[Version]:
        latest_versions = [self.get_most_recent_version(versions, index, supports_dataminer_collection) for index, version in enumerate(versions) if version.latest]
        return sorted(set(version for version in latest_versions if version is not None))
