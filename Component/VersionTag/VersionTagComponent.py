from typing import Sequence

from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import VersionTagTypedDict
from Component.Field.ComponentField import OptionalComponentField
from Component.Field.ComponentListField import ComponentListField
from Component.Field.Field import Field, InlinePermissions
from Component.Pattern import Pattern
from Component.VersionTag.LatestSlotComponent import LATEST_SLOT_PATTERN
from Component.VersionTag.VersionTagAutoAssignerComponent import (
    VERSION_TAG_AUTO_ASSIGNER_PATTERN,
)
from Utilities.Exceptions import VersionTagExclusivePropertyError
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)
from Version.VersionTag.VersionTag import VersionTag

VERSION_TAG_PATTERN:Pattern["VersionTagComponent"] = Pattern("is_version_tag")

class VersionTagComponent(Component[VersionTag]):

    class_name = "VersionTag"
    my_capabilities = Capabilities(is_version_tag=True)
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("auto_assign", False, ListTypeVerifier(dict, list)),
        TypedDictKeyTypeVerifier("development_name", False, str),
        TypedDictKeyTypeVerifier("is_development_tag", False, bool),
        TypedDictKeyTypeVerifier("is_fork_tag", False, bool),
        TypedDictKeyTypeVerifier("is_major_tag", False, bool),
        TypedDictKeyTypeVerifier("is_order_tag", False, bool),
        TypedDictKeyTypeVerifier("is_unreleased_tag", False, bool),
        TypedDictKeyTypeVerifier("latest_slot", False, str),
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

    def initialize_fields(self, data: VersionTagTypedDict) -> Sequence[Field]:
        self.is_development_tag = data.get("is_development_tag", False)
        self.development_name = data.get("development_name", "dev")
        self.is_fork_tag = data.get("is_fork_tag", False)
        self.is_order_tag = data.get("is_order_tag", False)
        self.is_major_tag = data.get("is_major_tag", False)
        self.is_unreleased_tag = data.get("is_unreleased_tag", False)

        self.auto_assigner_field = ComponentListField(data.get("auto_assign", ()), VERSION_TAG_AUTO_ASSIGNER_PATTERN, ("auto_assign",), allow_inline=InlinePermissions.mixed)
        self.latest_slot_field = OptionalComponentField(data.get("latest_slot", None), LATEST_SLOT_PATTERN, ("latest_slot",), allow_inline=InlinePermissions.reference, assume_component_group="latest_slots")
        return (self.auto_assigner_field, self.latest_slot_field)

    def create_final(self, trace:Trace) -> VersionTag:
        return VersionTag(
            name=self.name,
            development_name=self.development_name,
            is_development_tag=self.is_development_tag,
            is_fork_tag=self.is_fork_tag,
            is_order_tag=self.is_order_tag,
            is_major_tag=self.is_major_tag,
            is_unreleased_tag=self.is_unreleased_tag
        )

    def link_finals(self, trace:Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            latest_slot_component = self.latest_slot_field.subcomponent
            self.final.link_finals(
                latest_slot=latest_slot_component.final if latest_slot_component is not None else None,
            )

    def check(self, trace:Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().check(trace)
            if not self.is_order_tag:
                if self.latest_slot_field.subcomponent is not None:
                    trace.exception(VersionTagExclusivePropertyError("!is_order_tag", "latest_slot"))
                if self.is_major_tag:
                    trace.exception(VersionTagExclusivePropertyError("!is_order_tag", "is_major_tag"))
                if self.is_fork_tag:
                    trace.exception(VersionTagExclusivePropertyError("!is_order_tag", "is_fork_tag"))
                if self.is_development_tag:
                    trace.exception(VersionTagExclusivePropertyError("!is_order_tag", "is_development_tag"))
