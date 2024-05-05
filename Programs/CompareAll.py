import traceback
from typing import Generator, Iterable, TypeVar

import DataMiners.DataMiner as DataMiner
import DataMiners.DataMiners as DataMiners
import Version.VersionParser as VersionParser
import Structure.Normalizer as Normalizer
import Utilities.FileManager as FileManager
import Version.Version as Version
import Version.VersionTags as VersionTags

FlattenType = TypeVar("FlattenType")
def flatten(matrix:Iterable[Iterable[FlattenType]]) -> Generator[FlattenType, None, None]:
    yield from (item for row in matrix for item in row)

PairsType = TypeVar("PairsType")
def pairs(_list:Iterable[PairsType]) -> Generator[tuple[PairsType,PairsType], None, None]:
    previous_item = None
    for index, item in enumerate(_list):
        if index != 0:
            assert previous_item is not None
            yield (previous_item, item)
        previous_item = item

def compare(
        version1:Version.Version|None,
        version2:Version.Version,
        dataminer_collection:DataMiner.DataMinerCollection,
        undataminable_versions_between:list[Version.Version],
        normalizer_dependencies:Normalizer.NormalizerDependencies,
    ) -> None:
    dataminer_collection.compare(version1, version2, undataminable_versions_between, normalizer_dependencies)

def compare_all_of(
        dataminer_collection:DataMiner.DataMinerCollection,
        versions:list[Version.Version],
        exception_holder:dict[str,tuple[Exception,Version.Version|None,Version.Version|None]|bool],
        normalizer_dependencies:Normalizer.NormalizerDependencies,
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
            can_be_datamined = version.download_link is not None and not isinstance(dataminer_collection.get_version(version), DataMiner.NullDataMiner)
            if can_be_datamined:
                if previous_successful_version is not None:
                    compare(previous_successful_version, version, dataminer_collection, undataminable_versions_between, normalizer_dependencies)
                    normalizer_dependencies.forget(previous_successful_version)
                else: # First version that has this file.
                    compare(None, version, dataminer_collection, undataminable_versions_between, normalizer_dependencies)
                undataminable_versions_between = []
                previous_successful_version = version
            else:
                undataminable_versions_between.append(version)
    except Exception as e:
        assert version is not None
        print("%s failed at version %s." % (dataminer_collection.name, version.name))
        exception_holder[dataminer_collection.name] = (e, previous_successful_version, version)
    else:
        print("Compared all of %s." % dataminer_collection.name)
        exception_holder[dataminer_collection.name] = True

def select_dataminers(dataminers:list["DataMiner.DataMinerCollection"]) -> list["DataMiner.DataMinerCollection"]:
    dataminer_names = {dataminer.name: dataminer for dataminer in dataminers}
    selected_dataminer = None
    while selected_dataminer not in dataminer_names and selected_dataminer != "*":
        selected_dataminer = input("Choose a DataMiner to compare (%s or \"*\" for all): " % list(dataminer_names.keys()))
    if selected_dataminer == "*":
        return dataminers
    else:
        return [dataminer_names[selected_dataminer]]

def main() -> None:
    dataminers = DataMiners.dataminers
    selected_dataminers = select_dataminers(dataminers)
    versions = VersionParser.versions
    version_tags = VersionParser.version_tags
    major_tags = {tag for tag in version_tags.tags.values() if tag.is_major_tag}
    minor_tags_before = {tag for tag in version_tags.tags.values() if not tag.is_major_tag and tag in version_tags.order.tags_before_top_level_tag}
    minor_tags_after  = {tag for tag in version_tags.tags.values() if not tag.is_major_tag and tag in version_tags.order.tags_after_top_level_tag }
    major_versions:dict[Version.Version,list[Version.Version]] = {version: [] for version in versions.values() if version.ordering_tag in major_tags}
    for major_version, child_versions in major_versions.items():
        child_versions.extend(child for child in major_version.children if child.ordering_tag in minor_tags_before)
        child_versions.append(major_version)
        child_versions.extend(child for child in major_version.children if child.ordering_tag in minor_tags_after)

    sorted_versions = list(flatten(child_versions for child_versions in major_versions.values()))
    exception_holder:dict[str,bool|tuple[Exception,Version.Version|None,Version.Version|None]] = {dataminer_collection.name: False for dataminer_collection in selected_dataminers}
    normalizer_dependencies = Normalizer.NormalizerDependencies({}, dataminers)
    for dataminer_collection in selected_dataminers:
        compare_all_of(dataminer_collection, sorted_versions, exception_holder, normalizer_dependencies)

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
        raise RuntimeError("CompareAll threads excepted: %s" % [structure_name for structure_name, previous_version, version in excepted_threads])
    else:
        print("Compared all versions.")
