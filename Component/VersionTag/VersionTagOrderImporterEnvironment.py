from collections import Counter
from itertools import chain
from pathlib import Path
from typing import Any, Iterable

import Component.ComponentTyping as ComponentTyping
import Component.ImporterEnvironment as ImporterEnvironment
import Component.VersionTag.VersionTagOrderComponent as VersionTagOrderComponent
import Utilities.Exceptions as Exceptions
import Version.VersionTag.VersionTag as VersionTag
import Version.VersionTag.VersionTagOrder as VersionTagOrder


class VersionTagOrderImporterEnvironment(ImporterEnvironment.ImporterEnvironment[VersionTagOrder.VersionTagOrder]):

    assume_type = VersionTagOrderComponent.VersionTagOrderComponent.class_name

    single_component = True

    __slots__ = ()

    def get_default_contents(self) -> ComponentTyping.VersionTagOrderTypedDict:
        return {
            "allowed_children": {},
            "order": [],
            "tags_after_top_level_tag": [],
            "tags_before_top_level_tag": [],
            "top_level_tag": None,
        }

    def get_component_files(self) -> Iterable[Path]:
        return (self.domain.version_tags_order_file,)

    def get_component_group_name(self, file_path: Path) -> str:
        return "version_tags_order"

    def check(self, output: VersionTagOrder.VersionTagOrder, other_outputs: dict[str, Any]) -> list[Exception]:
        exceptions:list[Exception] = []
        version_tags:dict[str,VersionTag.VersionTag] = other_outputs[self.domain.name]["version_tags"]
        order_version_tags = [version_tag for version_tag in version_tags.values() if version_tag.is_order_tag]
        # all tags in output are guaranteed to be order tags because VersionTagOrderComponent made sure of it.

        order_tags_used:Counter[VersionTag.VersionTag] = Counter(
            order_tag
            for order_set in output.order
            for order_tag in order_set
        )
        exceptions.extend(
            Exceptions.NotAllOrderTagsUsedError(order_tag, "order") if times_used == 0
            else Exceptions.DuplicateVersionTagOrderError(order_tag, "order")
            for order_tag in order_version_tags
            if (times_used := order_tags_used[order_tag]) != 1
        )

        allowed_children = output.allowed_children
        exceptions.extend(
            Exceptions.NotAllOrderTagsUsedError(order_tag, "allowed_children")
            for order_tag in order_version_tags
            if order_tag not in allowed_children
        )
        for key_tag, children in allowed_children.items():
            already_children:set[VersionTag.VersionTag] = set()
            for child in children:
                if child in already_children:
                    exceptions.append(Exceptions.DuplicateVersionTagOrderError(child, ("allowed_children", key_tag.name)))
                already_children.add(child)

        if output.top_level_tag is not None:
            top_level_tags_used:Counter[VersionTag.VersionTag] = Counter(chain((output.top_level_tag,), output.tags_before_top_level_tag, output.tags_after_top_level_tag))
            exceptions.extend(
                Exceptions.NotAllOrderTagsUsedError(tag, "order") if times_used == 0
                else Exceptions.DuplicateVersionTagOrderError(tag, "order")
                for tag in chain((output.top_level_tag,), output.tags_before_top_level_tag, output.tags_after_top_level_tag)
                if (times_used := top_level_tags_used[tag]) != 1
            )

        return exceptions
