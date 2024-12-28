import traceback
from itertools import chain

import Component.Importer as Importer
import DataMiner.AbstractDataMinerCollection as AbstractDataMinerCollection
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.UserInput as UserInput
import Version.Version as Version

COMPARING_ENVIRONMENT = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.comparing)

def compare(
        version1:Version.Version|None,
        version2:Version.Version,
        dataminer_collection:AbstractDataMinerCollection.AbstractDataMinerCollection,
        undataminable_versions_between:list[Version.Version],
    ) -> None:
    dataminer_collection.compare(version1, version2, undataminable_versions_between, COMPARING_ENVIRONMENT)

def compare_all_of(
        dataminer_collection:AbstractDataMinerCollection.AbstractDataMinerCollection,
        versions:list[Version.Version],
        exception_holder:dict[str,tuple[Exception,Version.Version|None,Version.Version|None]|bool],
    ) -> None:
    previous_successful_version = None; version = None
    try:
        version = None
        previous_successful_version = None # The last Version that can be datamined for this file.
        undataminable_versions_between:list[Version.Version] = []
        comparison_parent = FileManager.get_comparison_file_path(dataminer_collection.name)
        if not comparison_parent.exists():
            comparison_parent.mkdir()
        for already_existing_comparison_file in comparison_parent.iterdir():
            already_existing_comparison_file.unlink()
        for version in versions:
            if dataminer_collection.supports_version(version):
                if previous_successful_version is not None:
                    compare(previous_successful_version, version, dataminer_collection, undataminable_versions_between)
                else: # First version that has this file.
                    compare(None, version, dataminer_collection, undataminable_versions_between)
                undataminable_versions_between = []
                previous_successful_version = version
                dataminer_collection.clear_some_caches()
                # must occur AFTER comparing.
            else:
                undataminable_versions_between.append(version)
    except Exception as e:
        if version is None:
            print("%s failed." % (dataminer_collection.name))
        else:
            print("%s failed at version %s." % (dataminer_collection.name, version.name))
        exception_holder[dataminer_collection.name] = (e, previous_successful_version, version)
    else:
        print("Compared all of %s." % dataminer_collection.name)
        exception_holder[dataminer_collection.name] = True
    finally:
        dataminer_collection.clear_caches()

def main() -> None:
    selected_dataminers = UserInput.input_multi(
        {dataminer_name: dataminer_collection for dataminer_name, dataminer_collection in Importer.dataminer_collections.items() if not dataminer_collection.comparing_disabled},
        "dataminer", allow_select_all=True, show_options_first_time=True, close_enough=True)
    versions = Importer.versions
    version_tags = Importer.version_tags
    version_tags_order = Importer.version_tags_order
    major_tags = {tag for tag in version_tags.values() if tag.is_major_tag}
    minor_tags_before = {tag for tag in version_tags.values() if not tag.is_major_tag and tag in version_tags_order.get_tags_before_top_level_tag()}
    minor_tags_after  = {tag for tag in version_tags.values() if not tag.is_major_tag and tag in version_tags_order.get_tags_after_top_level_tag()}
    major_versions:dict[Version.Version,list[Version.Version]] = {version: [] for version in versions.values() if version.get_order_tag() in major_tags}
    for major_version, child_versions in major_versions.items():
        child_versions.extend(child for child in major_version.children if child.get_order_tag() in minor_tags_before)
        child_versions.append(major_version)
        child_versions.extend(child for child in major_version.children if child.get_order_tag() in minor_tags_after)

    sorted_versions = list(chain.from_iterable(child_versions for child_versions in major_versions.values()))
    exception_holder:dict[str,bool|tuple[Exception,Version.Version|None,Version.Version|None]] = {dataminer_collection.name: False for dataminer_collection in selected_dataminers}
    for dataminer_collection in selected_dataminers:
        compare_all_of(dataminer_collection, sorted_versions, exception_holder)

    excepted = False
    excepted_threads:list[tuple[str,Version.Version|None,Version.Version|None]] = []
    for dataminer_name, completion in exception_holder.items():
        if isinstance(completion, tuple):
            excepted_threads.append((dataminer_name, completion[1], completion[2]))
            excepted = True
            print(dataminer_name)
            traceback.print_exception(completion[0])
            print()
    if excepted:
        for structure_name, previous_version, version in excepted_threads:
            print("\"%s\" excepted between Versions \"%s\" and \"%s\"" % (structure_name, previous_version, version))
        raise Exceptions.StructuresCompareFailureError([structure_name for structure_name, previous_version, version in excepted_threads])
    else:
        print("Compared all versions.")
