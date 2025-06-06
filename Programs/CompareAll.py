import traceback
from itertools import chain

import Domain.Domain as Domain
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Structure.StructureEnvironment import EnvironmentType, StructureEnvironment
from Utilities.Exceptions import StructuresCompareFailureError
from Utilities.UserInput import input_multi
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
        exception_holder:dict[str,tuple[Exception,Version|None,Version|None]|bool],
    ) -> None:
    previous_successful_version = None; version = None
    try:
        version = None
        previous_successful_version = None # The last Version that can be datamined for this file.
        undataminable_versions_between:list[Version] = []
        domain.comparisons_directory.mkdir(exist_ok=True)
        comparison_parent = domain.comparisons_directory.joinpath(dataminer_collection.name)
        if not comparison_parent.exists():
            comparison_parent.mkdir()
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
                dataminer_collection.clear_old_caches({dataminer_collection.get_structure_info(version)})
                # must occur AFTER comparing.
            else:
                undataminable_versions_between.append(version)
    except Exception as e:
        if version is None:
            print(f"{dataminer_collection.name} failed.")
        else:
            print(f"{dataminer_collection.name} failed at version {version.name}.")
        exception_holder[dataminer_collection.name] = (e, previous_successful_version, version)
    else:
        print(f"Compared all of {dataminer_collection.name}.")
        exception_holder[dataminer_collection.name] = True
    finally:
        dataminer_collection.clear_all_caches()

def main(domain:Domain.Domain) -> None:
    selected_dataminers = input_multi(
        {dataminer_name: dataminer_collection for dataminer_name, dataminer_collection in domain.dataminer_collections.items() if not dataminer_collection.comparing_disabled},
        "dataminer", allow_select_all=True, show_options_first_time=True, close_enough=True)
    versions = domain.versions
    version_tags = domain.version_tags
    version_tags_order = domain.version_tags_order
    major_tags = {tag for tag in version_tags.values() if tag.is_major_tag}
    minor_tags_before = {tag for tag in version_tags.values() if not tag.is_major_tag and tag in version_tags_order.tags_before_top_level_tag}
    minor_tags_after  = {tag for tag in version_tags.values() if not tag.is_major_tag and tag in version_tags_order.tags_after_top_level_tag}
    major_versions:dict[Version,list[Version]] = {version: [] for version in versions.values() if version.order_tag in major_tags}
    for major_version, child_versions in major_versions.items():
        child_versions.extend(child for child in major_version.children if child.order_tag in minor_tags_before)
        child_versions.append(major_version)
        child_versions.extend(child for child in major_version.children if child.order_tag in minor_tags_after)

    sorted_versions = list(chain.from_iterable(child_versions for child_versions in major_versions.values()))
    exception_holder:dict[str,bool|tuple[Exception,Version|None,Version|None]] = {dataminer_collection.name: False for dataminer_collection in selected_dataminers}
    for dataminer_collection in selected_dataminers:
        compare_all_of(domain, dataminer_collection, sorted_versions, exception_holder)

    excepted = False
    excepted_threads:list[tuple[str,Version|None,Version|None]] = []
    for dataminer_name, completion in exception_holder.items():
        if isinstance(completion, tuple):
            excepted_threads.append((dataminer_name, completion[1], completion[2]))
            excepted = True
            print(dataminer_name)
            traceback.print_exception(completion[0])
            print()
    if excepted:
        for structure_name, previous_version, version in excepted_threads:
            print(f"\"{structure_name}\" excepted between Versions \"{previous_version}\" and \"{version}\"")
        raise StructuresCompareFailureError([structure_name for structure_name, previous_version, version in excepted_threads])
    else:
        print("Compared all versions.")
