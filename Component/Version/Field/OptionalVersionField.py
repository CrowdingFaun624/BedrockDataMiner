import Component.Field.Field as Field
import Component.Field.OptionalComponentField as OptionalComponentField
import Component.Pattern as Pattern
import Component.Version.VersionComponent as VersionComponent
import Version.Version as Version

VERSION_PATTERN:Pattern.Pattern["VersionComponent.VersionComponent"] = Pattern.Pattern("is_version")

class OptionalVersionField(OptionalComponentField.OptionalComponentField["VersionComponent.VersionComponent"]):

    __slots__ = ()

    def __init__(self, subcomponent_data: str|None, path: list[str|int]) -> None:
        super().__init__(subcomponent_data, VERSION_PATTERN, path, allow_inline=Field.InlinePermissions.reference, assume_component_group="versions")

    @property
    def final(self) -> Version.Version|None:
        return None if self.subcomponent is None else self.subcomponent.final
