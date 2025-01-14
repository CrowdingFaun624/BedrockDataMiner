import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.OptionalComponentField as OptionalComponentField
import Component.Pattern as Pattern
import Component.VersionTag.LatestSlotComponent as LatestSlotComponent
import Component.VersionTag.VersionTagAutoAssignerComponent as VersionTagAutoAssignerComponent
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier
import Version.VersionTag.VersionTag as VersionTag

VERSION_TAG_AUTO_ASSIGNER_PATTERN:Pattern.Pattern["VersionTagAutoAssignerComponent.VersionTagAutoAssignerComponent"] = Pattern.Pattern("is_version_tag_auto_assigner")
LATEST_SLOT_PATTERN:Pattern.Pattern["LatestSlotComponent.LatestSlotComponent"] = Pattern.Pattern("is_latest_slot")

class VersionTagComponent(Component.Component[VersionTag.VersionTag]):

    class_name = "VersionTag"
    class_name_article = "a VersionTag"
    my_capabilities = Capabilities.Capabilities(is_version_tag=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("auto_assign", "a dict", False, TypeVerifier.ListTypeVerifier(dict, list, "a dict", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("development_name", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("is_development_tag", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("is_fork_tag", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("is_major_tag", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("is_order_tag", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("is_unreleased_tag", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("latest_slot", "a str", False, str),
    )

    __slots__ = (
        "auto_assigner_field",
        "development_name",
        "is_development_tag",
        "is_fork_tag",
        "is_major_tag",
        "is_order_tag",
        "is_unreleased_tag",
        "latest_slot_field",
    )

    def initialize_fields(self, data: ComponentTyping.VersionTagTypedDict) -> list[Field.Field]:
        self.is_development_tag = data.get("is_development_tag", False)
        self.development_name = data.get("development_name", "dev")
        self.is_fork_tag = data.get("is_fork_tag", False)
        self.is_order_tag = data.get("is_order_tag", False)
        self.is_major_tag = data.get("is_major_tag", False)
        self.is_unreleased_tag = data.get("is_unreleased_tag", False)

        self.auto_assigner_field = ComponentListField.ComponentListField(data.get("auto_assign", []), VERSION_TAG_AUTO_ASSIGNER_PATTERN, ["auto_assign"], allow_inline=Field.InlinePermissions.mixed)
        self.latest_slot_field = OptionalComponentField.OptionalComponentField(data.get("latest_slot", None), LATEST_SLOT_PATTERN, ["latest_slot"], allow_inline=Field.InlinePermissions.reference, assume_component_group="latest_slots")
        return [self.auto_assigner_field, self.latest_slot_field]

    def create_final(self) -> VersionTag.VersionTag:
        return VersionTag.VersionTag(
            name=self.name,
            development_name=self.development_name,
            is_development_tag=self.is_development_tag,
            is_fork_tag=self.is_fork_tag,
            is_order_tag=self.is_order_tag,
            is_major_tag=self.is_major_tag,
            is_unreleased_tag=self.is_unreleased_tag
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        latest_slot_component = self.latest_slot_field.subcomponent
        self.final.link_finals(
            latest_slot=latest_slot_component.final if latest_slot_component is not None else None,
        )
        return exceptions

    def check(self) -> list[Exception]:
        exceptions = super().check()
        if not self.is_order_tag:
            if self.latest_slot_field.subcomponent is not None:
                exceptions.append(Exceptions.VersionTagExclusivePropertyError(self, "!is_order_tag", "latest_slot"))
            if self.is_major_tag:
                exceptions.append(Exceptions.VersionTagExclusivePropertyError(self, "!is_order_tag", "is_major_tag"))
            if self.is_fork_tag:
                exceptions.append(Exceptions.VersionTagExclusivePropertyError(self, "!is_order_tag", "is_fork_tag"))
            if self.is_development_tag:
                exceptions.append(Exceptions.VersionTagExclusivePropertyError(self, "!is_order_tag", "is_development_tag"))
        return exceptions
