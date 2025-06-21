from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.Pattern import Pattern
from Version.VersionTag.VersionTagAutoAssigner import VersionTagAutoAssigner

VERSION_TAG_AUTO_ASSIGNER_PATTERN:Pattern["VersionTagAutoAssignerComponent"] = Pattern("is_version_tag_auto_assigner")

class VersionTagAutoAssignerComponent[T:VersionTagAutoAssigner=VersionTagAutoAssigner](Component[T]):

    class_name = "VersionTagAutoAssigner"
    my_capabilities = Capabilities(is_version_tag_auto_assigner=True)

    __slots__ = ()
