from typing import AbstractSet, Any, Mapping, Required, Sequence, TypedDict

from Component.Component import Component
from Utilities.Exceptions import NotAnOrderTagError
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)
from Version.VersionTag.VersionTag import VersionTag
from Version.VersionTag.VersionTagOrder import AllowedChildren, VersionTagOrder


class AllowedChildrenTypedDict(TypedDict):
    tag: Required[VersionTag]
    children: Required[Sequence[VersionTag]]

class AllowedChildrenComponent(Component[AllowedChildren, AllowedChildrenTypedDict]):

    type_name = "AllowedChildren"
    object_type = AllowedChildren
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("tag", True, VersionTag),
        TypedDictKeyTypeVerifier("children", True, ListTypeVerifier(VersionTag, list)),
    ))

    def link_final(self, fields: AllowedChildrenTypedDict) -> None:
        super().link_final(fields)
        self.final.link_allowed_children(
            children=fields["children"],
            tag=fields["tag"],
        )

class VersionTagOrderTypedDict(TypedDict):
    allowed_children: Required[Sequence[AllowedChildren]]
    order: Required[Sequence[Sequence[VersionTag]]]
    tags_after_top_level_tag: Required[Sequence[VersionTag]]
    tags_before_top_level_tag: Required[Sequence[VersionTag]]
    top_level_tag: Required[VersionTag | None]

class VersionTagOrderComponent(Component[VersionTagOrder, VersionTagOrderTypedDict]):

    type_name = "VersionTagOrder"
    object_type = VersionTagOrder
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("allowed_children", True, ListTypeVerifier(AllowedChildren, list)),
        TypedDictKeyTypeVerifier("order", True, ListTypeVerifier(ListTypeVerifier(VersionTag, list), list)),
        TypedDictKeyTypeVerifier("tags_after_top_level_tag", True, ListTypeVerifier(VersionTag, list)),
        TypedDictKeyTypeVerifier("tags_before_top_level_tag", True, ListTypeVerifier(VersionTag, list)),
        TypedDictKeyTypeVerifier("top_level_tag", True, (VersionTag, type(None))),
    ))

    def link_final(self, fields: VersionTagOrderTypedDict) -> None:
        super().link_final(fields)
        self.final.link_version_tag_order(
            allowed_children=fields["allowed_children"],
            order=fields["order"],
            tags_after_top_level_tag=fields["tags_after_top_level_tag"],
            tags_before_top_level_tag=fields["tags_before_top_level_tag"],
            top_level_tag=fields["top_level_tag"],
        )

    def post_check(self, fields: VersionTagOrderTypedDict, trace: Trace) -> bool:
        used_version_tag_components:set[VersionTag] = set()
        for order_set in fields["order"]:
            used_version_tag_components.update(order_set)
        for item in fields["allowed_children"]:
            used_version_tag_components.add(item.tag)
            used_version_tag_components.update(item.children)
        if fields["top_level_tag"] is not None:
            used_version_tag_components.add(fields["top_level_tag"])
        used_version_tag_components.update(fields["tags_after_top_level_tag"])
        used_version_tag_components.update(fields["tags_before_top_level_tag"])
        has_error:bool = False
        for used_version_tag_component in used_version_tag_components:
            with trace.enter_key(used_version_tag_component, ...):
                if not used_version_tag_component.is_order_tag:
                    trace.exception(NotAnOrderTagError(used_version_tag_component))
                    has_error = True
        return has_error
        # rest of checking is in ImporterFinalize

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        if super().finalize(propagating_booleans, propagating_sets, trace):
            return True
        self.final.finalize_version_tag_order()
        return False
