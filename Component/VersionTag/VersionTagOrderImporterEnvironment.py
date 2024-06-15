from typing import Any, Iterable

from pathlib2 import Path

import Component.Component as Component
import Component.ImporterEnvironment as ImporterEnvironment
import Component.VersionTag.VersionTagOrderComponent as VersionTagOrderComponent
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Version.VersionTag.VersionTag as VersionTag
import Version.VersionTag.VersionTagOrder as VersionTagOrder


class VersionTagOrderImporterEnvironment(ImporterEnvironment.ImporterEnvironment[VersionTagOrder.VersionTagOrder]):

    assume_type = VersionTagOrderComponent.VersionTagOrderComponent.class_name

    single_component = True

    def get_imports(self, components:dict[str,Component.Component], all_components:dict[str,dict[str,Component.Component]], name:str) -> dict[str,dict[str,Component.Component]]:
        return {"version_tags": all_components["version_tags"]}

    def get_component_files(self) -> Iterable[Path]:
        return [FileManager.VERSION_TAGS_ORDER_FILE]

    def get_component_group_name(self, file_path: Path) -> str:
        return "version_tags_order"

    def check(self, output: VersionTagOrder.VersionTagOrder, other_outputs: dict[str, Any]) -> list[Exception]:
        exceptions:list[Exception] = []
        version_tags:dict[str,VersionTag.VersionTag] = other_outputs["version_tags"]
        order_version_tags = [version_tag for version_tag in version_tags.values() if version_tag.is_order_tag]
        # all tags in output are guaranteed to be order tags because VersionTagOrderComponent made sure of it.

        order_tags_used:dict[VersionTag.VersionTag,int] = {order_tag: 0 for order_tag in order_version_tags}
        for order_set in output.get_order():
            for order_tag in order_set:
                order_tags_used[order_tag] += 1
        for order_tag, times_used in order_tags_used.items():
            if times_used == 0:
                exceptions.append(Exceptions.NotAllOrderTagsUsedError(order_tag, "order"))
            elif times_used > 1:
                exceptions.append(Exceptions.DuplicateVersionTagOrderError(order_tag, "order"))

        allowed_children = output.get_allowed_children()
        for order_tag in order_version_tags:
            if order_tag not in allowed_children:
                exceptions.append(Exceptions.NotAllOrderTagsUsedError(order_tag, "allowed_children"))
        for key_tag, children in allowed_children.items():
            already_children:set[VersionTag.VersionTag] = set()
            for child in children:
                if child in already_children:
                    exceptions.append(Exceptions.DuplicateVersionTagOrderError(child, ("allowed_children", key_tag.name)))
                already_children.add(child)

        top_level_tags_used:dict[VersionTag.VersionTag,int] = {order_tag: 0 for order_tag in order_version_tags}
        top_level_tags_used[output.get_top_level_tag()] += 1
        for tag_before in output.get_tags_before_top_level_tag():
            top_level_tags_used[tag_before] += 1
        for tag_after in output.get_tags_after_top_level_tag():
            top_level_tags_used[tag_after] += 1
        for tag, times_used in top_level_tags_used.items():
            if times_used == 0:
                exceptions.append(Exceptions.NotAllOrderTagsUsedError(tag, ("top_level_tag", "tags_before_top_level_tag", "tags_after_top_level_tag")))
            elif times_used > 1:
                exceptions.append(Exceptions.DuplicateVersionTagOrderError(tag, ("top_level_tag", "tags_before_top_level_tag", "tags_after_top_level_tag")))

        return exceptions
