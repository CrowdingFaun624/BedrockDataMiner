import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter
import Version.VersionProvider.LatestVersionProvider as LatestVersionProvider
import Version.VersionProvider.VersionProvider as VersionProvider

BUILT_IN_VERSION_PROVIDER_CLASSES:dict[str,type[VersionProvider.VersionProvider]] = {version_provider_class.__name__: version_provider_class for version_provider_class in [
    LatestVersionProvider.LatestVersionProvider,
]}

VERSION_PROVIDER_CLASSES = ScriptImporter.import_scripted_types("version_providers", BUILT_IN_VERSION_PROVIDER_CLASSES, VersionProvider.VersionProvider)

class VersionProviderField(Field.Field):

    __slots__ = (
        "version_provider",
    )

    def __init__(self, version_provider_name:str, path: list[str | int]) -> None:
        '''
        :version_provider_name: The name of the VersionProvider referenced by this Field.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.version_provider = VERSION_PROVIDER_CLASSES[version_provider_name]

    def get_final(self) -> type[VersionProvider.VersionProvider]:
        return self.version_provider
