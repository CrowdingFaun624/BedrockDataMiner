import Component.Importer as Importer
import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.FileDataMiner as FileDataMiner
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.FileManager as FileManager

def main() -> None:
    dataminer_collections = Importer.dataminer_collections
    all_files_dataminer = dataminer_collections["all_files"]
    versions = Importer.versions
    for version_index, version in enumerate(versions.values()):
        if not all_files_dataminer.supports_version(version):
            print("Skipped coverage report of %r (%i/%i) due to not supporting %r." % (version, version_index + 1, len(versions), all_files_dataminer))
            continue
        file_set:set[str] = set(all_files_dataminer.get_data_file(version))
        version_files_covered:set[str] = set()
        version_files_covered_dict:dict[DataMiner.DataMiner,set[str]] = {}
        for dataminer_collection in dataminer_collections.values():
            dataminer_settings = dataminer_collection.get_dataminer_settings(version)
            dataminer_class = dataminer_settings.get_dataminer_class()
            if not issubclass(dataminer_class, FileDataMiner.FileDataMiner):
                continue
            dataminer = dataminer_class(version, dataminer_settings)
            dependencies = DataMinerEnvironment.DataMinerDependencies({})
            for dependency_dataminer_collection in dataminer_settings.get_dependencies():
                dependency_dataminer_settings = dependency_dataminer_collection.get_dataminer_settings(version)
                dependency_dataminer = dependency_dataminer_settings.get_dataminer_class()(version, dependency_dataminer_settings)
                if isinstance(dependency_dataminer, FileDataMiner.FileDataMiner):
                    raise ValueError("%r has a FileDataMiner dependency (%r) in %r, which is not supported!" % (dataminer, dependency_dataminer, version))
                dependencies.set_item(dependency_dataminer.name, dependency_dataminer.get_data_file())
            environment = DataMinerEnvironment.DataMinerEnvironment(dependencies, StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.all_datamining))
            dataminer_files_covered = dataminer.get_coverage(file_set, environment)
            if len(overlapping_files := version_files_covered.intersection(dataminer_files_covered)) > 0:
                other_dataminers = [
                    other_dataminer
                    for other_dataminer, other_dataminer_coverage in version_files_covered_dict.items()
                    if len(other_dataminer_coverage | dataminer_files_covered) > 0
                ]
                raise RuntimeError("The following files in %r are covered by %r and dataminers [%s]: [%s]" % (version, dataminer, ", ".join(other_dataminer.name for other_dataminer in other_dataminers), ", ".join(overlapping_files)))
            version_files_covered.update(dataminer_files_covered)
            version_files_covered_dict[dataminer] = dataminer_files_covered
        leftover_files = file_set - version_files_covered
        file_path = "%s %s.txt" % (str(version_index).zfill(4), version.name)
        with open(FileManager.OUTPUT_DIRECTORY.joinpath(file_path), "wt") as f:
            f.write("\n".join(sorted(leftover_files)))
        print("Finished coverage report of %r (%i/%i)" % (version, version_index + 1, len(versions)))
    print("Finished all coverage reports")
