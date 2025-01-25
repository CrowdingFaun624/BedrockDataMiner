import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.Pattern as Pattern
import Component.Version.VersionComponent as VersionComponent

VERSION_TAG_AUTO_ASSIGNER_PATTERN:Pattern.Pattern["VersionTagAutoAssignerComponent"] = Pattern.Pattern("is_version_tag_auto_assigner")

class VersionTagAutoAssignerComponent(Component.Component[None]):

    class_name = "VersionTagAutoAssigner"
    my_capabilities = Capabilities.Capabilities(is_version_tag_auto_assigner=True)

    __slots__ = ()

    def contains_version(self, version:"VersionComponent.VersionComponent") -> bool:
        '''
        Returns True if this VersionTagAutoAssigner should assign its tag to this Version.
        :version: The Version to check for containment.
        '''
        ...
