from itertools import chain
from typing import Sequence

from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import VersionTagOrderTypedDict
from Component.Field.ComponentField import ComponentField, OptionalComponentField
from Component.Field.ComponentListField import ComponentListField
from Component.Field.Field import Field, InlinePermissions
from Component.Field.FieldListField import FieldListField
from Component.VersionTag.VersionTagComponent import (
    VERSION_TAG_PATTERN,
    VersionTagComponent,
)
from Utilities.Exceptions import NotAnOrderTagError
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)
from Version.VersionTag.VersionTagOrder import VersionTagOrder


class VersionTagOrderComponent(Component[VersionTagOrder]):

    class_name = "VersionTagOrder"
    my_capabilities = Capabilities()
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("allowed_children", True, DictTypeVerifier(dict, str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("order", True, ListTypeVerifier(ListTypeVerifier(str, list), list)),
        TypedDictKeyTypeVerifier("tags_after_top_level_tag", True, ListTypeVerifier(str, list)),
        TypedDictKeyTypeVerifier("tags_before_top_level_tag", True, ListTypeVerifier(str, list)),
        TypedDictKeyTypeVerifier("top_level_tag", True, (str, type(None))),
        TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "allowed_children_field",
        "order_field",
        "tags_after_top_level_tag",
        "tags_before_top_level_tag",
        "top_level_tag_field",
    )

    def initialize_fields(self, data: VersionTagOrderTypedDict) -> Sequence[Field]:
        self.order_field = FieldListField([
            ComponentListField(tags, VERSION_TAG_PATTERN, ("order", str(index)), allow_inline=InlinePermissions.reference, assume_component_group="version_tags")
            for index, tags in enumerate(data["order"])
        ], ("order",))
        self.allowed_children_field = [
            (
                ComponentField(key, VERSION_TAG_PATTERN, ("allowed_children", key), allow_inline=InlinePermissions.reference, assume_component_group="version_tags"),
                ComponentListField(children, VERSION_TAG_PATTERN, ("allowed_children", key), allow_inline=InlinePermissions.reference, assume_component_group="version_tags"),
            )
            for key, children in data["allowed_children"].items()
        ]
        self.top_level_tag_field = OptionalComponentField(data["top_level_tag"], VERSION_TAG_PATTERN, ("top_level_tag",), assume_component_group="version_tags")
        self.tags_before_top_level_tag = ComponentListField(data["tags_before_top_level_tag"], VERSION_TAG_PATTERN, ("tags_before_top_level_tag",), allow_inline=InlinePermissions.reference, assume_component_group="version_tags")
        self.tags_after_top_level_tag = ComponentListField(data["tags_after_top_level_tag"], VERSION_TAG_PATTERN, ("tags_after_top_level_tag",), allow_inline=InlinePermissions.reference, assume_component_group="version_tags")
        fields:list[Field] = [self.order_field, self.top_level_tag_field, self.tags_before_top_level_tag, self.tags_after_top_level_tag]
        fields.extend(chain.from_iterable(self.allowed_children_field))
        return fields

    def create_final(self, trace:Trace) -> VersionTagOrder:
        return VersionTagOrder(
            full_name=self.full_name,
        )

    def link_finals(self, trace:Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_finals(
                order=list(self.order_field.map(lambda component_list_field: set(component_list_field.map(lambda version_tag_component: version_tag_component.final)))),
                allowed_children={
                    key_field.subcomponent.final: list(
                        version_tag_component.final
                        for version_tag_component in children_field.subcomponents
                    ) for key_field, children_field in self.allowed_children_field
                },
                top_level_tag=self.top_level_tag_field.map(lambda subcomponent: subcomponent.final),
                tags_before_top_level_tag=list(self.tags_before_top_level_tag.map(lambda version_tag_component: version_tag_component.final)),
                tags_after_top_level_tag=list(self.tags_after_top_level_tag.map(lambda version_tag_component: version_tag_component.final)),
            )

    def check(self, trace:Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().check(trace)
            used_version_tag_components:set["VersionTagComponent"] = set()
            for order_set in self.order_field:
                used_version_tag_components.update(order_set.subcomponents)
            for key_field, children_field in self.allowed_children_field:
                used_version_tag_components.add(key_field.subcomponent)
                used_version_tag_components.update(children_field.subcomponents)
            if self.top_level_tag_field.subcomponent is not None:
                used_version_tag_components.add(self.top_level_tag_field.subcomponent)
            used_version_tag_components.update(self.tags_before_top_level_tag.subcomponents)
            used_version_tag_components.update(self.tags_after_top_level_tag.subcomponents)
            for used_version_tag_component in used_version_tag_components:
                with trace.enter_key(used_version_tag_component, ...):
                    if not used_version_tag_component.is_order_tag:
                        trace.exception(NotAnOrderTagError(used_version_tag_component.final))
            # rest of checking is in the ImporterEnvironment
