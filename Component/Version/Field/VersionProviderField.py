import Component.Field.Field as Field
import Domain.Domain as Domain
import Version.VersionProvider.VersionProvider as VersionProvider


class VersionProviderField(Field.Field):

    __slots__ = (
        "version_provider",
    )

    def __init__(self, version_provider_name:str, domain:"Domain.Domain", path: list[str | int]) -> None:
        '''
        :version_provider_name: The name of the VersionProvider referenced by this Field.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.version_provider = domain.version_provider_classes[version_provider_name]

    def get_final(self) -> type[VersionProvider.VersionProvider]:
        return self.version_provider
