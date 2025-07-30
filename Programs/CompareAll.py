import time
import traceback

import Domain.Domain as Domain
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Structure.StructureEnvironment import EnvironmentType, StructureEnvironment
from Utilities.Exceptions import StructuresCompareFailureError
from Utilities.MemoryUsage import memory_usage
from Utilities.UserInput import input_integer, input_multi, input_single
from Version.Version import Version


def initial_print(
    version:Version,
    dataminer_collection:AbstractDataminerCollection,
    domain:"Domain.Domain",
) -> None:
    environment = StructureEnvironment(EnvironmentType.comparing, domain)
    dataminer_collection.print_initial(version, environment)

def compare(
    version1:Version,
    version2:Version,
    dataminer_collection:AbstractDataminerCollection,
    undataminable_versions_between:list[Version],
    domain:"Domain.Domain",
) -> None:
    environment = StructureEnvironment(EnvironmentType.comparing, domain)
    dataminer_collection.compare(version1, version2, undataminable_versions_between, environment)

def compare_all_of(
        domain:Domain.Domain,
        dataminer_collection:AbstractDataminerCollection,
        versions:list[Version],
        *,
        previous_successful_version:Version|None=None, # The last Version that can be datamined for this file.
        destroy_previous:bool=True,
    ) -> tuple[Exception, Version|None, Version|None]|None:
    version = None
    print(f"Comparing all of {dataminer_collection.name}.")
    try:
        undataminable_versions_between:list[Version] = []
        domain.comparisons_directory.mkdir(exist_ok=True)
        comparison_parent = domain.comparisons_directory.joinpath(dataminer_collection.name)
        if not comparison_parent.exists():
            comparison_parent.mkdir()
        if destroy_previous:
            for already_existing_comparison_file in comparison_parent.iterdir():
                already_existing_comparison_file.unlink()
        for version in versions:
            if dataminer_collection.supports_version(version):
                if previous_successful_version is not None:
                    compare(previous_successful_version, version, dataminer_collection, undataminable_versions_between, domain)
                else: # First version that has this file.
                    initial_print(version, dataminer_collection, domain)
                undataminable_versions_between = []
                previous_successful_version = version
                dataminer_collection.clear_old_caches({(version, dataminer_collection.get_structure_info(version))}) # must occur AFTER comparing.
                memory_usage.adjust()
            else:
                undataminable_versions_between.append(version)
            version.close_accessors()
            memory_usage.adjust()
    except Exception as e:
        if version is None:
            print(f"{dataminer_collection.name} failed.")
        else:
            print(f"{dataminer_collection.name} failed at version {version.name}.")
        output = (e, previous_successful_version, version)
    else:
        output = None
    finally:
        dataminer_collection.clear_all_caches()
        memory_usage.adjust()
    return output

def main(domain:Domain.Domain) -> None:
    versions = domain.versions
    latest_versions = [version for version in versions.values() if version.latest]
    selected_dataminers = input_multi(
        {dataminer_name: dataminer_collection for dataminer_name, dataminer_collection in domain.dataminer_collections.items() if not dataminer_collection.comparing_disabled},
        "dataminer", allow_select_all=True, show_options_first_time=True, close_enough=True,
        alternative_selectors={"^": lambda: [
            dataminer_collection.name
            for dataminer_collection in domain.dataminer_collections.values()
            if not dataminer_collection.comparing_disabled and any(dataminer_collection.supports_version(version) for version in latest_versions)
        ]}
    )
    sorted_versions = list(versions.values())

    exceptions:dict[AbstractDataminerCollection,tuple[Exception,Version|None,Version|None]] = {}
    start_time = time.time()
    for dataminer_collection in selected_dataminers:
        exception_tuple = compare_all_of(domain, dataminer_collection, sorted_versions)
        if exception_tuple is not None:
            exceptions[dataminer_collection] = exception_tuple
    finish_time = time.time()

    memory_usage.reset()
    for dataminer_collection, (exception, version1, version2) in exceptions.items():
        print(f"\"{dataminer_collection.name}\" excepted between Versions \"{version1}\" and \"{version2}\"")
        traceback.print_exception(exception)
        print()
    if len(exceptions) > 0:
        raise StructuresCompareFailureError([dataminer_collection.name for dataminer_collection in exceptions.keys()])
    else:
        print(f"Compared all versions in {finish_time - start_time:.3f} seconds.")

def compare_some(domain:Domain.Domain) -> None:
    versions = domain.versions
    selected_dataminer = input_single({dataminer_name: dataminer_collection for dataminer_name, dataminer_collection in domain.dataminer_collections.items() if not dataminer_collection.comparing_disabled},
        "dataminer", show_options_first_time=True, close_enough=True)
    start_version = input_single(versions, "start Version")
    print("The previous viable Version is the latest Version before the start Version that supports the dataminer_collection")
    previous_successful_version = input_single(versions, "previous viable Version")
    start_id = input_integer("starting file", may_be_negative=False, may_be_zero=True)
    domain.comparison_file_counts[selected_dataminer.name] = start_id - 1 # -1 because the next id will be the stored one + 1.
    all_versions = list(versions.values())
    start_index = all_versions.index(start_version)
    sorted_versions = all_versions[start_index:]

    start_time = time.time()
    exception_tuple = compare_all_of(domain, selected_dataminer, sorted_versions, previous_successful_version=previous_successful_version, destroy_previous=False)
    finish_time = time.time()

    memory_usage.reset()
    if exception_tuple is not None:
        exception, version1, version2 = exception_tuple
        print(f"\"{selected_dataminer.name}\" excepted between Versions \"{version1}\" and \"{version2}\"")
        traceback.print_exception(exception)
        raise StructuresCompareFailureError([selected_dataminer.name])
    else:
        print(f"Compared all versions after {start_version.name} in {finish_time - start_time:.3f} seconds.")
