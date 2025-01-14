import datetime
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, cast

import Component.Component as Component
import Component.ImporterEnvironment as ImporterEnvironment
import Component.Version.VersionComponent as VersionComponent
import Utilities.Exceptions as Exceptions
import Version.Version as Version
import Version.VersionFileType as VersionFileType
import Version.VersionTag.VersionTag as VersionTag
import Version.VersionTag.VersionTagOrder as VersionTagOrder


class VersionImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,Version.Version]]):

    assume_type = VersionComponent.VersionComponent.class_name

    __slots__ = ()

    def get_component_files(self) -> Iterable[Path]:
        return (self.domain.versions_file,)

    def get_component_group_name(self, file_path: Path) -> str:
        return "versions"

    def get_assumed_used_components(self, components:dict[str,Component.Component], name:str) -> Iterable[Component.Component]:
        return components.values()

    def finalize(self, output:dict[str, Version.Version], other_outputs:dict[str,Any]) -> None:
        version_tags:dict[str,VersionTag.VersionTag] = other_outputs[self.domain.name]["version_tags"]
        latest_tags:defaultdict[str,set[VersionTag.VersionTag]] = defaultdict(lambda: set())
        for version_tag in version_tags.values():
            if version_tag.latest_slot is not None:
                latest_tags[version_tag.latest_slot].add(version_tag)

        for latest_slot_tags in latest_tags.values():
            for version in reversed(output.values()):
                if version.released and version.order_tag in latest_slot_tags:
                    version.latest = True
                    if version.parent is not None:
                        version.parent.latest = True
                    break
        if self.domain.versions_directory.exists():
            versions_without_directory:list[bool] = [False] * len(output)
            for version_directory in self.domain.versions_directory.iterdir():
                if (version_directory_name := version_directory.name) in output:
                    versions_without_directory[output[version_directory_name].index] = True
                else:
                    try:
                        version_directory.rmdir()
                    except OSError:
                        print(f"Version directory \"{version_directory_name}\" does not exists in versions.json and contains files!")
        else:
            versions_without_directory:list[bool] = [True] * len(output)
        if len(output) > 0:
            self.domain.versions_directory.mkdir(exist_ok=True)
        for version, has_directory in zip(output.values(), versions_without_directory):
            if has_directory: continue
            version.version_directory.mkdir()

    def check(self, output: dict[str, Version.Version], other_outputs: dict[str, Any]) -> list[Exception]:
        exceptions = super().check(output, other_outputs)
        version_tag_ordering:VersionTagOrder.VersionTagOrder = other_outputs[self.domain.name]["version_tags_order"]
        version_tags:dict[str,VersionTag.VersionTag] = other_outputs[self.domain.name]["version_tags"]
        ORDERING_TAGS = [version_tag for version_tag in version_tags.values() if version_tag.is_order_tag]
        ORDER = version_tag_ordering.order
        ALLOWED_CHILDREN = version_tag_ordering.allowed_children
        TOP_LEVEL_TAG = version_tag_ordering.top_level_tag
        BEFORE_TAGS = version_tag_ordering.tags_before_top_level_tag
        AFTER_TAGS = version_tag_ordering.tags_after_top_level_tag

        top_level_versions:list[Version.Version] = [] # versions with no parents
        for version in output.values():
            if (order_tag_count := sum(order_tag in version.tags for order_tag in ORDERING_TAGS)) != 1:
                exceptions.append(Exceptions.VersionOrderingTagsError(version, order_tag_count, version.tags))
            if version.parent is None:
                top_level_versions.append(version)

        top_level_childrens:list[Version.Version] = []
        for version in top_level_versions:
            top_level_childrens.extend(version.get_children_recursive())
        if len(set(top_level_childrens)) != len(top_level_childrens):
            already_seen_versions:set[Version.Version] = set()
            for version in top_level_childrens:
                if version in already_seen_versions: exceptions.append(Exceptions.VersionChildOfMultipleTopLevelVersionsError(version))
                else: already_seen_versions.add(version)
            else: raise Exceptions.InvalidStateError("A duplicate version exists, but unable to find it!")

        if TOP_LEVEL_TAG is not None:
            exceptions.extend(
                Exceptions.VersionTopLevelError(version, TOP_LEVEL_TAG)
                for version in top_level_versions
                if TOP_LEVEL_TAG not in version.tags
            )
        exceptions.extend(
            Exceptions.VersionChildError(version, version.order_tag, child, child.order_tag)
            for version in output.values()
            for child in version.children
            if child.order_tag not in ALLOWED_CHILDREN[version.order_tag]
        )

        def order_contains_at_index(ordering_tag:VersionTag.VersionTag) -> bool:
            order_at_index = ORDER[order_index]
            if isinstance(order_at_index, set):
                return ordering_tag in order_at_index
            else:
                return ordering_tag == order_at_index

        for version in output.values():
            order_index = 0
            for child in version.children:
                while not order_contains_at_index(child.order_tag):
                    order_index += 1
                    if order_index >= len(ORDER):
                        exceptions.append(Exceptions.VersionChildOrderError(version, [child.order_tag for child in version.children], child))
                        break
                if order_index >= len(ORDER): break
                # after this while loop, `order_index` must be a value such that child.ordering_tag == or in ORDER[order_index].
        versions_without_timezone:dict[Version.Version, datetime.datetime] = {}
        version_with_timezone:tuple[Version.Version, datetime.datetime]|None = None
        for version in output.values():
            if version.time is not None:
                if version.time.tzinfo is None:
                    versions_without_timezone[version] = version.time
                else:
                    version_with_timezone = (version, version.time)
        if version_with_timezone is not None:
            exceptions.extend(Exceptions.VersionTimezoneError(version, time, version_with_timezone[0], version_with_timezone[1]) for version, time in versions_without_timezone.items())
        else:
            for version in output.values():
                previous_time = None
                previous_child = None # for error messages
                for child in version.children:
                    if child.order_tag in BEFORE_TAGS:
                        if version.time is not None and child.time is not None and child.time > version.time:
                            exceptions.append(Exceptions.VersionOrderSequenceError(version, version.order_tag, child, child.order_tag, "after"))
                    elif child.order_tag in AFTER_TAGS:
                        if version.time is not None and child.time is not None and child.time < version.time:
                            exceptions.append(Exceptions.VersionOrderSequenceError(version, version.order_tag, child, child.order_tag, "before"))
                    if previous_time is not None:
                        if previous_child is None:
                            exceptions.append(Exceptions.InvalidStateError("previous_child is None but previous_time is not None!"))
                            continue
                        if child.time is not None and child.time < previous_time:
                            exceptions.append(Exceptions.VersionTimeTravelError(previous_child, previous_time, child, child.time, version))
                    previous_time = child.time
                    previous_child = child

        # some VersionFiles cannot exist if an unreleased VersionTag exists on the Version.
        # some VersionFileTypes require a VersionFile to exist on every Version.
        version_file_types = cast(dict[str,VersionFileType.VersionFileType], other_outputs[self.domain.name]["version_file_types"])
        required_version_file_types = {version_file_type_name: version_file_type for version_file_type_name, version_file_type in version_file_types.items() if version_file_type.must_exist}
        exceptions.extend(
            Exceptions.UnreleasedDownloadableVersionError(version, version_file)
            for version in output.values()
            if not version.released
            for version_file in version.version_files
            if version_file.has_accessors() and not version_file.version_file_type.available_when_unreleased
        )
        for version in output.values():
            version_files = version.version_files_dict
            exceptions.extend(
                Exceptions.RequiredVersionFileTypeMissingError(required_version_file_type, version)
                for required_version_file_type_name, required_version_file_type in required_version_file_types.items()
                if required_version_file_type_name not in version_files
            )
        return exceptions
