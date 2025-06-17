import time
import traceback
from collections import defaultdict
from itertools import pairwise
from typing import AbstractSet, Sequence

from ordered_set import OrderedSet

import Domain.Domain as Domain
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Structure.Structure import Structure
from Structure.Uses import UsageTracker, Use
from Utilities.Exceptions import StructuresUsageFailureError
from Utilities.FileManager import OUTPUT_DIRECTORY, PARENT_DIRECTORY
from Utilities.MemoryUsage import memory_usage
from Utilities.UserInput import input_multi
from Version.Version import Version


def get_version_order(versions:Sequence[Version]) -> Sequence[Version]:
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

def get_dataminer_collection_groups(dataminer_collections:list[AbstractDataminerCollection]) -> Sequence[Sequence[AbstractDataminerCollection]]:
    # groups AbstractDataminerCollections by their Structure.
    output:defaultdict[Structure, list[AbstractDataminerCollection]] = defaultdict(lambda: [])
    for dataminer_collection in dataminer_collections:
        output[dataminer_collection.structure].append(dataminer_collection)
    return list(output.values())

def get_usage_of(dataminer_collections:Sequence[AbstractDataminerCollection], used_uses:OrderedSet[Use], versions:Sequence[Version], usage_tracker:UsageTracker) -> tuple[Exception, Version|None]|None:
    supported_versions = [version for version in versions if any(dataminer_collection.supports_version(version) for dataminer_collection in dataminer_collections)]
    version_order = get_version_order(supported_versions)
    version:Version|None = None
    try:
        for version in version_order:
            if usage_tracker.everything_used(dataminer_collections[0].structure): break
            for dataminer_collection in dataminer_collections:
                if dataminer_collection.supports_version(version):
                    used_uses.update(dataminer_collection.get_uses(version, usage_tracker))
                    memory_usage.adjust()
            dataminer_collection.clear_old_caches({dataminer_collection.get_structure_info(version)})
            # Because AbstractDataminerCollections are grouped by Structure, the above statement works on all AbstractDataminerCollections at once.
            version.close_accessors()
            print(f"\t{version}")
    except Exception as e:
        if version is None:
            print(f"{", ".join(dataminer_collection.name for dataminer_collection in dataminer_collections)} failed.")
        else:
            print(f"{", ".join(dataminer_collection.name for dataminer_collection in dataminer_collections)} failed at version {version.name}.")
        output = (e, version)
    else:
        output = None
        print(f"Got usage of {", ".join(dataminer_collection.name for dataminer_collection in dataminer_collections)}")
    finally:
        memory_usage.adjust()
        dataminer_collection.clear_all_caches()
    return output

def main(domain:"Domain.Domain") -> None:
    dataminer_collections = input_multi(domain.dataminer_collections, "dataminer", allow_select_all=True, show_options_first_time=True, close_enough=True)
    used_uses:OrderedSet[Use] = OrderedSet(())

    all_uses:OrderedSet[Use] = OrderedSet(())
    for dataminer_collection in dataminer_collections:
        all_uses.update(dataminer_collection.get_all_uses())
    usage_tracker = UsageTracker([dataminer_collection.structure for dataminer_collection in dataminer_collections], all_uses)
    versions = list(domain.versions.values())

    exceptions:list[tuple[Sequence[AbstractDataminerCollection],tuple[Exception,Version|None]]] = []
    start_time = time.time()
    dataminer_collection_groups = get_dataminer_collection_groups(dataminer_collections)
    for dataminer_collection_group in dataminer_collection_groups:
        exception_tuple = get_usage_of(dataminer_collection_group, used_uses, versions, usage_tracker)
        if exception_tuple is not None:
            exceptions.append((dataminer_collection_group, exception_tuple))
    finish_time = time.time()

    memory_usage.reset()
    for dataminer_collection_group, (exception, version) in exceptions:
        print(f"{", ".join(dataminer_collection.name for dataminer_collection in dataminer_collections)} excepted at Version \"{version}\"")
        traceback.print_exception(exception)
        print()
    if len(exceptions) > 0:
        raise StructuresUsageFailureError([dataminer_collection.name for dataminer_collection_group, _ in exceptions for dataminer_collection in dataminer_collection_group])
    else:
        message = f"Got all usage in {finish_time - start_time:.3f} seconds."
        print(message)

    unused_uses:AbstractSet[Use] = all_uses - used_uses
    unused_length = sum(1 for use in unused_uses if use.should_display(unused_uses))
    all_length = len(all_uses)
    if len(evil_uses := (used_uses - all_uses)) > 0:
        print(evil_uses)
    summary = f"Found {unused_length} unused out of {all_length} possible. ({len(evil_uses)} evil)"
    del all_uses

    document:list[str] = []
    document.append(message)
    document.append(summary)
    document.extend(use.message() for use in unused_uses if use.should_display(unused_uses))
    if len(evil_uses) > 0: # "evil uses" indicate that there is a bug
        document.append("START EVIL USES")
        document.extend(use.message() for use in evil_uses)
        document.append("END EVIL USES")
    document.append(message)
    document.append(summary) # used twice

    string_document = "\n".join(document)
    output_path = OUTPUT_DIRECTORY.joinpath("structure_usage_report.txt")
    with open(output_path, "wt") as f:
        f.write(string_document)
    if len(document) < 5000:
        print(string_document)
    else:
        print(summary)
    print(f"Wrote output to \"{output_path.relative_to(PARENT_DIRECTORY).as_posix()}\".")
