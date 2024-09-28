import traceback

import Component.Importer as Importer
import DataMiner.DataMinerCollection as DataMinerCollection
import DataMiner.DataMiners as DataMiners
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Exceptions as Exceptions
import Version.Version as Version

STRUCTURE_ENVIRONMENT = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.all_datamining)

def datamine_version(version:Version.Version, all_dataminers:dict[str,DataMinerCollection.DataMinerCollection], print_messages:bool=True) -> None:
    dataminers = DataMiners.get_dataminable_dataminers(version)
    already_files = set(DataMiners.currently_has_data_files_from(version))
    needed_files = [dataminer for dataminer in dataminers if dataminer not in already_files]
    if len(needed_files) == 0:
        if print_messages:
            print("Skipped \"%s\" due to already being complete." % (version.name))
        return # All of this Version's data files are already there.
    if print_messages:
        print("Started \"%s\"." % (version.name))
    failure_dataminers = DataMiners.run(version, needed_files, STRUCTURE_ENVIRONMENT, all_dataminers)
    if len(failure_dataminers) > 0:
        for failed_dataminer, exception in failure_dataminers:
            print("\nFailed to datamine \"%s\" for \"%s\":" % (failed_dataminer.name, version.name))
            traceback.print_exception(exception)
        print()
        raise Exceptions.DataMinersFailureError(version, [dataminer_tuple[0] for dataminer_tuple in failure_dataminers])
    if not version.latest:
        for version_file in version.get_version_files():
            for accessor in version_file.get_accessors():
                accessor.all_done() # remove all of the installed client files from the version directory so I don't have to clog my storage

def main() -> None:
    dataminers_dict = {dataminer.name: dataminer for dataminer in DataMiners.dataminers}
    for version in reversed(Importer.versions.values()):
        if not any(dataminer_collection.supports_version(version) for dataminer_collection in dataminers_dict.values()):
            print("Skipped \"%s\" due to being unarchived." % (version.name))
        else:
            datamine_version(version, dataminers_dict)
    print("Datamined all versions.")
