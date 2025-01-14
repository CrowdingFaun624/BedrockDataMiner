import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter
import Domain.Domain as Domain
import Version.VersionProvider.VersionProvider as VersionProvider


class VersionProviderField(Field.Field):

    __slots__ = (
        "version_provider",
        "version_provider_name",
    )

    def __init__(self, version_provider_name:str, domain:"Domain.Domain", path: list[str | int]) -> None:
        '''
        :version_provider_name: The name of the VersionProvider referenced by this Field.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.version_provider_name = version_provider_name
        self.version_provider:type[VersionProvider.VersionProvider]


    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        global_components:dict[str,dict[str,dict[str,"Component.Component"]]],
        functions:ScriptImporter.ScriptSetSetSet,
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["Component.Component"],list["Component.Component"]]:
        self.version_provider = functions.version_provider_classes.get(self.version_provider_name, source_component, self.error_path)
        return [], []
