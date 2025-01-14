import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.Version.VersionComponent as VersionComponent


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
