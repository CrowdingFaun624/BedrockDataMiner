import time
import traceback
from collections import defaultdict
from datetime import datetime
from functools import reduce
from itertools import pairwise
from operator import or_
from typing import AbstractSet, Callable, Generator, Sequence

from ordered_set import OrderedSet

import Domain.Domain as Domain
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Structure.Structure import Structure
from Structure.StructureBase import StructureBase
from Structure.Uses import UsageTracker, Use
from Utilities.FileManager import OUTPUT_DIRECTORY, PARENT_DIRECTORY
from Utilities.MemoryUsage import memory_usage
from Utilities.UserInput import input_multi
from Version.Version import Version


def get_version_suborder(versions:Sequence[Version]) -> Sequence[Version]:
    if len(versions) < 2:
        return versions
    output:list[Version] = []
    used_indices:set[int] = set()

    next_iteration:list[int] # ordered largest to smallest
    next_set:set[int]
    this_iteration:list[int] = [len(versions) - 1, 0]
    new_iteration:list[int] = this_iteration.copy()
    while len(new_iteration) > 0:
        for index in new_iteration:
            if index in used_indices: continue
            output.append(versions[index])
            used_indices.add(index)

        new_iteration = []
        next_iteration = []
        next_set = set()
        for index1, index2 in pairwise(this_iteration):
            if index1 not in next_set:
                next_iteration.append(index1)
            next_set.add(index1)
            num = (index1 + index2) // 2
            if num in next_set:
                continue
            next_iteration.append(num)
            next_set.add(num)
            if num in used_indices:
                continue
            new_iteration.append(num)
        if this_iteration[-1] not in next_set:
            next_iteration.append(this_iteration[-1])

        this_iteration = next_iteration
    return output

def get_version_order(all_versions:Sequence[Version], dataminer_collections:Sequence[AbstractDataminerCollection]) -> Generator[Version, set[AbstractDataminerCollection], None]:
    current_output:set[Version] = set()
    finished_dataminer_collections:set[AbstractDataminerCollection] = set()

    while True:
        version_supports = [
            (version, {
                dataminer_collection
                for dataminer_collection in dataminer_collections
                if dataminer_collection not in finished_dataminer_collections and dataminer_collection.supports_version(version)
            }) for version in all_versions
            if version not in current_output
        ]
        count_versions:dict[int, list[Version]] = defaultdict(lambda: [])
        for version, supported_dataminer_collections in version_supports:
            count_versions[len(supported_dataminer_collections)].append(version)
        sorted_versions:Sequence[tuple[int, Sequence[Version]]] = [(supported_count, versions) for supported_count, versions in sorted(count_versions.items(), key=lambda item: item[0], reverse=True)]
        new_finished_dataminer_collections:set[AbstractDataminerCollection] = set()

        any_versions_remaining = False
        for supported_count, versions in sorted_versions:
            if supported_count == 0: continue
            for version in get_version_suborder(versions):
                any_versions_remaining = True
                new_finished_dataminer_collections = yield version
                current_output.add(version)
                if len(new_finished_dataminer_collections) > 0:
                    finished_dataminer_collections.update(new_finished_dataminer_collections)
                    break
            if len(new_finished_dataminer_collections) > 0: break
        if len(finished_dataminer_collections) == len(dataminer_collections) or not any_versions_remaining:
            break

def get_dataminer_collection_groups(all_dataminer_collections:list[AbstractDataminerCollection]) -> Sequence[Sequence[AbstractDataminerCollection]]:
    # groups AbstractDataminerCollections by their descendant Structures.
    # If there is any common Structure between two StructureBases' descendants, they will be in the same group.
    output:list[tuple[list[AbstractDataminerCollection], set[Structure]]] = []
    for dataminer_collection in all_dataminer_collections:
        descendants = dataminer_collection.structure.get_descendants(set())
        for dataminer_collections, child_structures in output:
            if dataminer_collection.structure in child_structures or any(descendant in child_structures for descendant in descendants):
                dataminer_collections.append(dataminer_collection)
                child_structures.update(descendants)
                break
        else:
            output.append(([dataminer_collection], descendants))
    return [dataminer_collections for dataminer_collections, _ in output]

def get_usage_of(
    dataminer_collections:Sequence[AbstractDataminerCollection],
    used_uses:OrderedSet[Use],
    versions:Sequence[Version],
    usage_tracker:UsageTracker,
    create_new_report_function:Callable[[],None]
) -> tuple[Exception, Version|None]|None:
    version_order = get_version_order(versions, dataminer_collections)
    print(f"Starting usage of {", ".join(dataminer_collection.name for dataminer_collection in dataminer_collections)}")
    unfinished_dataminer_collections:set[AbstractDataminerCollection] = set(dataminer_collections)
    last_time = time.time()

    all_structures_used:dict[StructureBase, list[AbstractDataminerCollection]] = defaultdict(lambda: [])
    for dataminer_collection in dataminer_collections:
        all_structures_used[dataminer_collection.structure].append(dataminer_collection)

    version:Version = next(version_order)
    try:
        while True:
            if len(unfinished_dataminer_collections) == 0: break
            structures_used:dict[StructureBase, list[AbstractDataminerCollection]] = defaultdict(lambda: [])

            for dataminer_collection in dataminer_collections:
                if dataminer_collection in unfinished_dataminer_collections and dataminer_collection.supports_version(version):
                    structures_used[dataminer_collection.structure].append(dataminer_collection)
                    used_uses.update(dataminer_collection.get_uses(version, usage_tracker))
                    memory_usage.adjust()

            for _, structure_dataminer_collections in structures_used.items():
                structure_dataminer_collections[0].clear_old_caches({(version, dataminer_collection.get_structure_info(version)) for dataminer_collection in structure_dataminer_collections})
            version.close_accessors()

            print(f"\t{version}")
            if (time.time() - last_time) > 60:
                create_new_report_function()
                last_time = time.time()

            new_finished_dataminer_collections:set[AbstractDataminerCollection] = set()
            for structure, structure_dataminer_collections in all_structures_used.items():
                if usage_tracker.everything_used((structure,)):
                    new_finished_dataminer_collections.update(dataminer_collection for dataminer_collection in structure_dataminer_collections if dataminer_collection in unfinished_dataminer_collections)
                    unfinished_dataminer_collections.difference_update(structure_dataminer_collections)

            try:
                version = version_order.send(new_finished_dataminer_collections)
            except StopIteration:
                break

    except Exception as e:
        if version is None:
            print(f"{", ".join(dataminer_collection.name for dataminer_collection in dataminer_collections)} failed.")
        else:
            print(f"{", ".join(dataminer_collection.name for dataminer_collection in dataminer_collections)} failed at version {version.name}.")
        output = (e, version)
    else:
        output = None
    finally:
        memory_usage.adjust()
        dataminer_collection.clear_all_caches()
    return output

def get_report_message(
    exceptions:list[tuple[Sequence[AbstractDataminerCollection],tuple[Exception,Version|None]]],
    dataminer_collections:Sequence[AbstractDataminerCollection],
    complete:bool,
    duration:float,
) -> tuple[Sequence[str], Sequence[str]]:
    message:list[str] = []
    extended_message:list[str] = []
    if not complete:
        message.append(f"IN PROGRESS AT {datetime.isoformat(datetime.now())}: [{", ".join(dataminer_collection.name for dataminer_collection in dataminer_collections)}] COMPLETED")
    if len(exceptions) > 0:
        names = [dataminer_collection.name for dataminer_collection_group, _ in exceptions for dataminer_collection in dataminer_collection_group]
        message.append(f"Failed to get usage on DataminerCollections [{", ".join(names)}] (len {len(names)}) in {duration:.3f} seconds.")
        for dataminer_collection_group, (exception, version) in exceptions:
            extended_message.append(f"{", ".join(dataminer_collection.name for dataminer_collection in dataminer_collection_group)} excepted at Version \"{version}\"")
            extended_message.extend(line.rstrip("\n") for line in traceback.format_exception(exception))
            extended_message.append("\n")
    else:
        message.append(f"Got usage in {duration:.3f} seconds.")
    return message, extended_message

def create_report(
    all_uses:OrderedSet[Use], # From all AbstractDataminerCollections thus scanned.
    dataminer_collections:Sequence[AbstractDataminerCollection], # All AbstractDataminerCollections thus scanned.
    used_uses:OrderedSet[Use],
    exceptions:list[tuple[Sequence[AbstractDataminerCollection],tuple[Exception,Version|None]]],
    duration:float,
    complete:bool,
    print_report:bool,
) -> None:
    message, extended_message = get_report_message(exceptions, dataminer_collections, complete, duration)

    unused_uses:AbstractSet[Use] = all_uses - used_uses
    unused_length = sum(1 for use in unused_uses if use.should_display(unused_uses))
    all_length = len(all_uses)
    evil_uses = used_uses - all_uses
    summary = f"Found {unused_length} unused out of {all_length} possible.{f" ({len(evil_uses)} evil)" if len(evil_uses) > 0 else ""}"

    document:list[str] = []
    document.extend(message)
    document.append(summary)
    document.extend(use.message() for use in unused_uses if use.should_display(unused_uses))
    if len(evil_uses) > 0: # "evil uses" indicate that there is a bug
        document.append("START EVIL USES")
        document.extend(use.message() for use in evil_uses)
        document.append("END EVIL USES")
    document.extend(message)
    document.extend(extended_message)
    document.append(summary) # used twice

    string_document = "\n".join(document)
    output_path = OUTPUT_DIRECTORY.joinpath("structure_usage_report.txt")
    with open(output_path, "wt") as f:
        f.write(string_document)
    if print_report:
        if len(document) < 5000:
            print(string_document)
        else:
            print(summary)
        print(f"Wrote output to \"{output_path.relative_to(PARENT_DIRECTORY).as_posix()}\".")

def main(domain:"Domain.Domain") -> None:
    dataminer_collections = input_multi(domain.dataminer_collections, "dataminer", allow_select_all=True, show_options_first_time=True, close_enough=True)
    used_uses:OrderedSet[Use] = OrderedSet(())

    dataminer_collection_all_uses:dict[StructureBase,OrderedSet[Use]] = {}
    for dataminer_collection in dataminer_collections:
        if dataminer_collection.structure not in dataminer_collection_all_uses:
            dataminer_collection_all_uses[dataminer_collection.structure] = dataminer_collection.get_all_uses()
    all_uses = OrderedSet(reduce(or_, dataminer_collection_all_uses.values(), OrderedSet(())))
    usage_tracker = UsageTracker([dataminer_collection.structure for dataminer_collection in dataminer_collections], all_uses, domain)
    versions = list(domain.versions.values())

    cumulative_structures:set[StructureBase] = set()
    cumulative_uses:OrderedSet[Use] = OrderedSet(())
    cumulative_dataminer_collections:list[AbstractDataminerCollection] = []
    exceptions:list[tuple[Sequence[AbstractDataminerCollection],tuple[Exception,Version|None]]] = []
    create_new_report_function = lambda: create_report(cumulative_uses, cumulative_dataminer_collections, used_uses, exceptions, time.time() - start_time, False, False)
    start_time = time.time()
    dataminer_collection_groups = get_dataminer_collection_groups(dataminer_collections)

    for dataminer_collection_group in dataminer_collection_groups:
        for dataminer_collection in dataminer_collection_group:
            if dataminer_collection.structure not in cumulative_structures:
                cumulative_structures.add(dataminer_collection.structure)
                cumulative_uses.update(dataminer_collection_all_uses[dataminer_collection.structure])

        exception_tuple = get_usage_of(dataminer_collection_group, used_uses, versions, usage_tracker, create_new_report_function)
        cumulative_dataminer_collections.extend(dataminer_collection_group)
        if exception_tuple is not None:
            exceptions.append((dataminer_collection_group, exception_tuple))

        create_new_report_function()
    finish_time = time.time()

    memory_usage.reset()
    create_report(all_uses, dataminer_collections, used_uses, exceptions, finish_time - start_time, True, True)
