import Component.Field.Field as Field
import Component.Field.OptionalComponentField as OptionalComponentField
import Component.Pattern as Pattern
import Component.VersionTag.VersionTagComponent as VersionTagComponent
import Version.VersionTag.VersionTag as VersionTag

VERSION_TAG_PATTERN:Pattern.Pattern["VersionTagComponent.VersionTagComponent"] = Pattern.Pattern("is_version_tag")

class OptionalVersionTagField(OptionalComponentField.OptionalComponentField[VersionTagComponent.VersionTagComponent]):

    def __init__(self, subcomponent_data: str|None, path: list[str | int]) -> None:
        super().__init__(subcomponent_data, VERSION_TAG_PATTERN, path, allow_inline=Field.InlinePermissions.reference)

    @property
    def final(self) -> VersionTag.VersionTag|None:
        return None if self.subcomponent is None else self.subcomponent.final
