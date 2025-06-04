from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Version.Version import Version
from Version.VersionProvider.VersionProvider import VersionProvider


class LatestVersionProvider(VersionProvider):

    def get_versions(self, versions: list[Version], *, supports_dataminer_collection:AbstractDataminerCollection) -> list[Version]:
        return [version for version in versions if version.latest and supports_dataminer_collection.supports_version(version)]
