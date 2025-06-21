from collections import Counter, defaultdict
from datetime import datetime
from itertools import chain
from typing import Callable, Sequence

import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
from Component.Group import Group
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Dataminer.DataminerCollection import DataminerCollection
from Dataminer.DataminerSettings import DataminerSettings
from Utilities.Trace import Trace
from Version.Version import Version
from Version.VersionFileType import VersionFileType
from Version.VersionTag.VersionTag import VersionTag
from Version.VersionTag.VersionTagOrder import VersionTagOrder


def finalize_versions(all_components:dict["Domain.Domain", list[Group]], trace:Trace) -> None:
    for domain, groups in all_components.items():
        with trace.enter(domain, domain.name, ...):
            finalize_versions_domain(groups, domain, trace)

def finalize_versions_domain(groups:list[Group], domain:"Domain.Domain", trace:Trace) -> None:
    version_tags:list[VersionTag] = []
    versions:dict[str,Version] = {}
    for group in groups:
        for component_name, component in group.components.items():
            match component.final:
                case VersionTag():
                    version_tags.append(component.final)
                case Version():
                    versions[component_name] = component.final

    latest_tags:defaultdict[str,set[VersionTag]] = defaultdict(lambda: set())
    for version_tag in version_tags:
        if version_tag.latest_slot is not None:
            latest_tags[version_tag.latest_slot].add(version_tag)

    for latest_slot_tags in latest_tags.values():
        for version in reversed(versions.values()):
            if version.released and version.order_tag in latest_slot_tags:
                version.latest = True
                if version.parent is not None and version.order_tag.is_development_tag:
                    version.parent.latest = True
                break
    if domain.versions_directory.exists():
        versions_without_directory:list[bool] = [False] * len(versions)
        for version_directory in domain.versions_directory.iterdir():
            if (version_directory_name := version_directory.name) in versions:
                versions_without_directory[versions[version_directory_name].index] = True
            else:
                try:
                    version_directory.rmdir()
                except OSError:
                    print(f"Version directory \"{version_directory_name}\" does not exists in versions.json and contains files!")
    else:
        versions_without_directory:list[bool] = [True] * len(versions)
    if len(versions) > 0:
        domain.versions_directory.mkdir(exist_ok=True)
    for version, has_directory in zip(versions.values(), versions_without_directory):
        if has_directory: continue
        version.version_directory.mkdir()

def check_versions(all_components:dict["Domain.Domain",list[Group]], trace:Trace) -> None:
    for domain, groups in all_components.items():
        with trace.enter(domain, domain.name, ...):
            check_versions_domain(groups, domain, trace)

def check_versions_domain(groups:list[Group], domain:"Domain.Domain", trace:Trace) -> None:
    version_tags:list[VersionTag] = []
    versions:dict[str,Version] = {}
    version_tag_orders:list[VersionTagOrder] = []
    version_file_types:list[VersionFileType] = []
    for group in groups:
        for component_name, component in group.components.items():
            match component.final:
                case VersionTag():
                    version_tags.append(component.final)
                case Version():
                    versions[component_name] = component.final
                case VersionTagOrder():
                    version_tag_orders.append(component.final)
                case VersionFileType():
                    version_file_types.append(component.final)
    if len(version_tag_orders) == 0:
        return
    elif len(version_tag_orders) > 1:
        raise Exceptions.ComponentCountError(version_tag_orders, VersionTagOrder)

    ORDERING_TAGS = [version_tag for version_tag in version_tags if version_tag.is_order_tag]
    ORDER = version_tag_orders[0].order
    ALLOWED_CHILDREN = version_tag_orders[0].allowed_children
    TOP_LEVEL_TAG = version_tag_orders[0].top_level_tag
    BEFORE_TAGS = version_tag_orders[0].tags_before_top_level_tag
    AFTER_TAGS = version_tag_orders[0].tags_after_top_level_tag

    top_level_versions:list[Version] = [] # versions with no parents
    for version in versions.values():
        with trace.enter_key(version, ...):
            if (order_tag_count := sum(order_tag in version.tags for order_tag in ORDERING_TAGS)) != 1:
                trace.exception(Exceptions.VersionOrderingTagsError(version, order_tag_count, version.tags))
            if version.parent is None:
                top_level_versions.append(version)

    top_level_childrens:list[Version] = []
    for version in top_level_versions:
        top_level_childrens.extend(version.get_children_recursive())
    if len(set(top_level_childrens)) != len(top_level_childrens):
        already_seen_versions:set[Version] = set()
        for version in top_level_childrens:
            with trace.enter_key(version, ...):
                if version in already_seen_versions: trace.exception(Exceptions.VersionChildOfMultipleTopLevelVersionsError(version))
                else: already_seen_versions.add(version)
        else: raise Exceptions.InvalidStateError("A duplicate version exists, but unable to find it!")

    if TOP_LEVEL_TAG is not None:
        trace.exceptions(
            Exceptions.VersionTopLevelError(version, TOP_LEVEL_TAG)
            for version in top_level_versions
            if TOP_LEVEL_TAG not in version.tags
        )
    trace.exceptions(
        Exceptions.VersionChildError(version, version.order_tag, child, child.order_tag)
        for version in versions.values()
        for child in version.children
        if child.order_tag not in ALLOWED_CHILDREN[version.order_tag]
    )

    def order_contains_at_index(ordering_tag:VersionTag) -> bool:
        order_at_index = ORDER[order_index]
        if isinstance(order_at_index, set):
            return ordering_tag in order_at_index
        else:
            return ordering_tag == order_at_index

    for version in versions.values():
        with trace.enter_key(version, ...):
            order_index = 0
            for child in version.children:
                while not order_contains_at_index(child.order_tag):
                    order_index += 1
                    if order_index >= len(ORDER):
                        trace.exception(Exceptions.VersionChildOrderError(version, [child.order_tag for child in version.children], child))
                        break
                if order_index >= len(ORDER): break
                # after this while loop, `order_index` must be a value such that child.ordering_tag == or in ORDER[order_index].
    versions_without_timezone:dict[Version, datetime] = {}
    version_with_timezone:tuple[Version, datetime]|None = None
    for version in versions.values():
        if version.time is not None:
            if version.time.tzinfo is None:
                versions_without_timezone[version] = version.time
            else:
                version_with_timezone = (version, version.time)
    if version_with_timezone is not None:
        trace.exceptions(Exceptions.VersionTimezoneError(version, time, version_with_timezone[0], version_with_timezone[1]) for version, time in versions_without_timezone.items())
    else:
        for version in versions.values():
            with trace.enter_key(version, ...):
                previous_time = None
                previous_child = None # for error messages
                for child in version.children:
                    if child.order_tag in BEFORE_TAGS:
                        if version.time is not None and child.time is not None and child.time > version.time:
                            trace.exception(Exceptions.VersionOrderSequenceError(version, version.order_tag, child, child.order_tag, "after"))
                    elif child.order_tag in AFTER_TAGS:
                        if version.time is not None and child.time is not None and child.time < version.time:
                            trace.exception(Exceptions.VersionOrderSequenceError(version, version.order_tag, child, child.order_tag, "before"))
                    if previous_time is not None:
                        if previous_child is None:
                            trace.exception(Exceptions.InvalidStateError("previous_child is None but previous_time is not None!"))
                            continue
                        if child.time is not None and child.time < previous_time:
                            trace.exception(Exceptions.VersionTimeTravelError(previous_child, previous_time, child, child.time, version))
                    previous_time = child.time
                    previous_child = child

    # some VersionFiles cannot exist if an unreleased VersionTag exists on the Version.
    # some VersionFileTypes require a VersionFile to exist on every Version.
    required_version_file_types = {version_file_type.name: version_file_type for version_file_type in version_file_types if version_file_type.must_exist}
    trace.exceptions(
        Exceptions.UnreleasedDownloadableVersionError(version, version_file)
        for version in versions.values()
        if not version.released
        for version_file in version.version_files
        if version_file.has_accessors() and not version_file.version_file_type.available_when_unreleased
    )
    for version in versions.values():
        with trace.enter_key(version, ...):
            version_files = version.version_files_dict
            trace.exceptions(
                Exceptions.RequiredVersionFileTypeMissingError(required_version_file_type, version)
                for required_version_file_type_name, required_version_file_type in required_version_file_types.items()
                if required_version_file_type_name not in version_files
            )

def get_dependencies(dataminer_settings:DataminerSettings, dataminer_settings_dict:dict[DataminerCollection,DataminerSettings], already:set[str]) -> Sequence[str]:
    if dataminer_settings.name in already:
        return (dataminer_settings.name,)
    already.add(dataminer_settings.name)
    duplicated_dataminer_settings:list[str] = []
    for dependency in dataminer_settings.dependencies:
        if not isinstance(dependency, DataminerCollection):
            # if it's not a DataminerCollection, its dependencies cannot vary on version.
            continue
        already_copy = already.copy()
        duplicated_dataminer_settings.extend(get_dependencies(dataminer_settings_dict[dependency], dataminer_settings_dict, already_copy))
    return duplicated_dataminer_settings

def check_for_loops(used_versions:set[Version], dataminer_collections:Sequence[AbstractDataminerCollection], trace:Trace) -> None:
    '''Raises an error if a loop exists in any part.'''
    versions = sorted(used_versions)
    for version in versions:
        all_dataminer_settings = {dataminer_collection: dataminer_collection.get_dataminer_settings(version) for dataminer_collection in dataminer_collections if isinstance(dataminer_collection, DataminerCollection)}
        trace.exceptions(
            Exceptions.DataminerSettingsImporterLoopError(dataminer_settings, duplicated_datminer_settings)
            for dataminer_settings in all_dataminer_settings.values()
            if len(duplicated_datminer_settings := get_dependencies(dataminer_settings, all_dataminer_settings, set())) > 0
        )

def check_for_duplicate_file_names(dataminers:Sequence[AbstractDataminerCollection], trace:Trace) -> None:
    names:dict[str,AbstractDataminerCollection] = {}
    duplicate_name_groups:dict[str,list[AbstractDataminerCollection]] = {}
    for dataminer in dataminers:
        if dataminer.file_name in names:
            if dataminer.file_name not in duplicate_name_groups:
                duplicate_name_groups[dataminer.file_name] = [names[dataminer.file_name]]
            duplicate_name_groups[dataminer.file_name].append(dataminer)
        else:
            names[dataminer.file_name] = dataminer
    trace.exceptions(
        Exceptions.DataminerDuplicateFileNameError(name, duplicate_dataminers)
        for name, duplicate_dataminers in duplicate_name_groups.items()
    )

def check_dataminer_collections(all_components:dict["Domain.Domain", list[Group]], trace:Trace) -> None:
    dataminer_collections:Sequence[AbstractDataminerCollection] = [
        component.final
        for groups in all_components.values()
        for group in groups
        for component in group.components.values()
        if isinstance(component.final, AbstractDataminerCollection)
    ]
    used_versions:set[Version] = set()
    for dataminer_collection in dataminer_collections:
        if not isinstance(dataminer_collection, DataminerCollection): continue
        for dataminer_settings in dataminer_collection.dataminer_settings:
            start_version = dataminer_settings.version_range.start
            stop_version = dataminer_settings.version_range.stop
            if start_version is not None:
                used_versions.add(start_version)
            if stop_version is not None:
                used_versions.add(stop_version)
    check_for_loops(used_versions, dataminer_collections, trace)
    check_for_duplicate_file_names(dataminer_collections, trace)

def check_version_tag_order(all_components:dict["Domain.Domain",list[Group]], trace:Trace) -> None:
    for domain, groups in all_components.items():
        with trace.enter(domain, domain.name, ...):
            check_version_tag_order_domain(groups, domain, trace)

def check_version_tag_order_domain(groups:list[Group], domain:"Domain.Domain", trace:Trace) -> None:
    version_tags:list[VersionTag] = []
    version_tag_orders:list[VersionTagOrder] = []
    for group in groups:
        for component_name, component in group.components.items():
            match component.final:
                case VersionTag():
                    version_tags.append(component.final)
                case VersionTagOrder():
                    version_tag_orders.append(component.final)
    if len(version_tag_orders) == 0:
        return
    elif len(version_tag_orders) > 1:
        raise Exceptions.ComponentCountError(version_tag_orders, VersionTagOrder)
    version_tag_order = version_tag_orders[0]

    order_version_tags = [version_tag for version_tag in version_tags if version_tag.is_order_tag]
    # all tags in output are guaranteed to be order tags because VersionTagOrderComponent made sure of it.

    order_tags_used:Counter[VersionTag] = Counter(
        order_tag
        for order_set in version_tag_order.order
        for order_tag in order_set
    )
    trace.exceptions(
        Exceptions.NotAllOrderTagsUsedError(order_tag, "order") if times_used == 0
        else Exceptions.DuplicateVersionTagOrderError(order_tag, "order")
        for order_tag in order_version_tags
        if (times_used := order_tags_used[order_tag]) != 1
    )

    allowed_children = version_tag_order.allowed_children
    trace.exceptions(
        Exceptions.NotAllOrderTagsUsedError(order_tag, "allowed_children")
        for order_tag in order_version_tags
        if order_tag not in allowed_children
    )
    for key_tag, children in allowed_children.items():
        with trace.enter_key(key_tag, children):
            already_children:set[VersionTag] = set()
            for child in children:
                if child in already_children:
                    trace.exception(Exceptions.DuplicateVersionTagOrderError(child, ("allowed_children", key_tag.name)))
                already_children.add(child)

    if version_tag_order.top_level_tag is not None:
        top_level_tags_used:Counter[VersionTag] = Counter(chain((version_tag_order.top_level_tag,), version_tag_order.tags_before_top_level_tag, version_tag_order.tags_after_top_level_tag))
        trace.exceptions(
            Exceptions.NotAllOrderTagsUsedError(tag, "order") if times_used == 0
            else Exceptions.DuplicateVersionTagOrderError(tag, "order")
            for tag in chain((version_tag_order.top_level_tag,), version_tag_order.tags_before_top_level_tag, version_tag_order.tags_after_top_level_tag)
            if (times_used := top_level_tags_used[tag]) != 1
        )

finalizers:Sequence[Callable[[dict["Domain.Domain",list[Group]],Trace],None]] = [
    finalize_versions,
    check_versions,
    check_dataminer_collections,
    check_version_tag_order,
]

def finalize_all(all_components:dict["Domain.Domain",list[Group]], primary_domain:"Domain.Domain", print_exceptions:Callable[["Domain.Domain", Trace],None]) -> None:
    trace = Trace()
    for finalizer in finalizers:
        finalizer(all_components, trace)
    print_exceptions(primary_domain, trace)
