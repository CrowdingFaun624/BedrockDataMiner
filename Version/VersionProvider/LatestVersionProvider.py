import Dataminer.AbstractDataminerCollection as AbstractDataminerCollection
import Version.Version as Version
import Version.VersionProvider.VersionProvider as VersionProvider


class LatestVersionProvider(VersionProvider.VersionProvider):

    def get_versions(self, versions: list[Version.Version], *, supports_dataminer_collection:AbstractDataminerCollection.AbstractDataminerCollection) -> list[Version.Version]:
        return [version for version in versions if version.latest and supports_dataminer_collection.supports_version(version)]
