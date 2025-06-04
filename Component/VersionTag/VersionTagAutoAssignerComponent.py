from typing import TYPE_CHECKING

from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.Pattern import Pattern

if TYPE_CHECKING:
    from Component.Version.VersionComponent import VersionComponent

VERSION_TAG_AUTO_ASSIGNER_PATTERN:Pattern["VersionTagAutoAssignerComponent"] = Pattern("is_version_tag_auto_assigner")

class VersionTagAutoAssignerComponent(Component[None]):

    class_name = "VersionTagAutoAssigner"
    my_capabilities = Capabilities(is_version_tag_auto_assigner=True)

    __slots__ = ()

    def contains_version(self, version:"VersionComponent") -> bool:
        '''
        Returns True if this VersionTagAutoAssigner should assign its tag to this Version.
        :version: The Version to check for containment.
        '''
        ...
