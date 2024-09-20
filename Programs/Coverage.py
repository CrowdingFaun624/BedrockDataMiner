from typing import cast

import Component.Importer as Importer
import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerCollection as DataMinerCollection
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.FileDataMiner as FileDataMiner
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.FileManager as FileManager
import Version.Version as Version


def do_dataminer_collection(
    dataminer_collection:DataMinerCollection.DataMinerCollection  ,
    version:Version.Version,
    dependencies:DataMinerEnvironment.DataMinerDependencies,
    file_set:set[str],
    version_files_covered:set[str],
    version_files_covered_dict:dict[DataMiner.DataMiner,set[str]],
) -> None:
    dataminer_settings = dataminer_collection.get_dataminer_settings(version)
    dataminer_class = dataminer_settings.get_dataminer_class()
    if not issubclass(dataminer_class, FileDataMiner.FileDataMiner):
        return
    dataminer = dataminer_class(version, dataminer_settings)
    for dependency_dataminer_collection in dataminer_settings.get_dependencies():
        if dependencies.has_item(dependency_dataminer_collection.name): continue
        dependency_dataminer_settings = dependency_dataminer_collection.get_dataminer_settings(version)
        dependency_dataminer_class = dependency_dataminer_settings.get_dataminer_class()
        if issubclass(dependency_dataminer_class, DataMiner.NullDataMiner):
            raise ValueError("%r has a NullDataMiner dependency %r for %r!" % (dataminer, dependency_dataminer_settings, version))
        dependency_dataminer = dependency_dataminer_class(version, dependency_dataminer_settings)
        if isinstance(dependency_dataminer, FileDataMiner.FileDataMiner):
            raise ValueError("%r has a FileDataMiner dependency (%r) in %r, which is not supported!" % (dataminer, dependency_dataminer, version))
        dependencies.set_item(dependency_dataminer.name, dependency_dataminer.get_data_file())
    environment = DataMinerEnvironment.DataMinerEnvironment(dependencies, StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.all_datamining))
    dataminer_files_covered = dataminer.get_coverage(file_set, environment)
    if len(overlapping_files := version_files_covered.intersection(dataminer_files_covered)) > 0:
        other_dataminers = [
            other_dataminer
            for other_dataminer, other_dataminer_coverage in version_files_covered_dict.items()
            if len(other_dataminer_coverage.intersection(dataminer_files_covered)) > 0
        ]
        raise RuntimeError("The following files in %r are covered by %r and dataminers [%s]: [%s]" % (version, dataminer, ", ".join(repr(other_dataminer) for other_dataminer in other_dataminers), ", ".join(overlapping_files)))
    version_files_covered.update(dataminer_files_covered)
    version_files_covered_dict[dataminer] = dataminer_files_covered

def do_version(version:Version.Version, all_files_dataminer:DataMinerCollection.DataMinerCollection, version_index:int, total_versions:int, dataminer_collections:dict[str,DataMinerCollection.DataMinerCollection]) -> None:
    if not all_files_dataminer.supports_version(version):
        print("Skipped coverage report of %r (%i/%i) due to not supporting %r." % (version, version_index, total_versions, all_files_dataminer))
        return
    print("Starting coverage report of %r (%i/%i)" % (version, version_index, total_versions))
    file_set:set[str] = set(file for file in cast(list[str], all_files_dataminer.get_data_file(version)) if not file.endswith(".brarchive"))
    version_files_covered:set[str] = set()
    version_files_covered_dict:dict[DataMiner.DataMiner,set[str]] = {}
    dependencies = DataMinerEnvironment.DataMinerDependencies({})
    for dataminer_collection in dataminer_collections.values():
        do_dataminer_collection(dataminer_collection, version, dependencies, file_set, version_files_covered, version_files_covered_dict)
    leftover_files = file_set - version_files_covered
    file_path = "%s %s.txt" % (str(version_index).zfill(4), version.name)
    with open(FileManager.OUTPUT_DIRECTORY.joinpath(file_path), "wt") as f:
        f.write("\n".join(sorted(leftover_files)))

def pick_version(versions:dict[str,Version.Version]) -> tuple[Version.Version, int]:
    while True:
        user_input = input("Which version name? ")
        if user_input in versions:
            version = versions[user_input]
            break
        else: continue
    version_index = len(versions) - version.index - 1
    return version, version_index

def do_all() -> None:
    for file in FileManager.OUTPUT_DIRECTORY.iterdir():
        file.unlink()
    dataminer_collections = Importer.dataminer_collections
    all_files_dataminer = dataminer_collections["all_files"]
    versions = Importer.versions
    for version_index, version in enumerate(reversed(versions.values())):
        do_version(version, all_files_dataminer, version_index, len(versions), dataminer_collections)
    print("Finished all coverage reports")

def do_one() -> None:
    dataminer_collections = Importer.dataminer_collections
    all_files_dataminer = dataminer_collections["all_files"]
    versions = Importer.versions
    version, version_index = pick_version(versions)
    do_version(version, all_files_dataminer, version_index, len(versions), dataminer_collections)

def do_before() -> None:
    dataminer_collections = Importer.dataminer_collections
    all_files_dataminer = dataminer_collections["all_files"]
    versions = Importer.versions
    target_version, target_version_index = pick_version(versions)
    for version_index, version in enumerate(reversed(versions.values())):
        if version_index < target_version_index: continue
        do_version(version, all_files_dataminer, version_index, len(versions), dataminer_collections)

def search() -> None:
    search_term = input("Search term: ")
    for file in FileManager.OUTPUT_DIRECTORY.iterdir():
        with open(file, "rt") as f:
            contents = f.readlines()
        count = 0
        for content in contents:
            if search_term in content:
                count += 1
        if count > 0:
            print(file.stem, count)

def main() -> None:
    functions = {
        "all": do_all,
        "before": do_before,
        "one": do_one,
        "search": search
    }
    user_input = None
    while user_input not in functions:
        user_input = input("Choose from [%s]: " % (", ".join(functions.keys())))
    functions[user_input]()
