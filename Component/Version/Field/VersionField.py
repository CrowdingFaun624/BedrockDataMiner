from typing import TYPE_CHECKING

import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Version.Version as Version

if TYPE_CHECKING:
    import Component.Version.VersionComponent as VersionComponent

VERSION_PATTERN:Pattern.Pattern[VersionComponent.VersionComponent] = Pattern.Pattern([{"is_version": True}])

class VersionField(ComponentField.ComponentField["VersionComponent.VersionComponent"]):

    __slots__ = ()

    def __init__(self, subcomponent_data: str, path: list[str|int]) -> None:
        super().__init__(subcomponent_data, VERSION_PATTERN, path, allow_inline=Field.InlinePermissions.reference)

    def get_final(self) -> Version.Version:
        return self.get_component().get_final()
