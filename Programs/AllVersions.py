import traceback

import DataMiners.DataMiner as DataMiner
import DataMiners.DataMiners as DataMiners
import Structure.StructureEnvironment as StructureEnvironment
import Version.Version as Version
import Version.VersionParser as VersionParser

STRUCTURE_ENVIRONMENT = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.all_datamining)

def datamine_version(version:Version.Version, all_dataminers:dict[str,DataMiner.DataMinerCollection], print_messages:bool=True) -> bool:
    dataminers = DataMiners.get_dataminable_dataminers(version, all_dataminers)
    already_files = set(DataMiners.currently_has_data_files_from(version))
    needed_files = [dataminer for dataminer in dataminers if dataminer not in already_files]
    if len(needed_files) == 0:
        if print_messages:
            print("Skipped \"%s\" due to already being complete." % (version.name))
        return True # All of this Version's data files are already there.
    if print_messages:
        print("Started \"%s\"." % (version.name))
    failure_dataminers = DataMiners.run(version, needed_files, STRUCTURE_ENVIRONMENT, all_dataminers)
    if len(failure_dataminers) > 0:
        for failed_dataminer, exception in failure_dataminers:
            print("\nFailed to datamine \"%s\" for \"%s\":" % (failed_dataminer.name, version.name))
            traceback.print_exception(exception)
        print()
        raise RuntimeError("Failed to datamine version \"%s\"!" % (version.name))
    if not version.latest:
        for version_file in version.version_files.values():
            for accessor in version_file.accessors.values():
                accessor.all_done() # remove all of the installed client files from the version folder so I don't have to clog my storage
    return True

def main() -> None:
    dataminers_dict = {dataminer.name: dataminer for dataminer in DataMiners.dataminers}
    for version in reversed(VersionParser.versions.values()):
        if len(version.version_files) == 0:
            print("Skipped \"%s\" due to being unarchived." % (version.name))
        else:
            all_dataminers_success = datamine_version(version, dataminers_dict)
            if not all_dataminers_success:
                raise RuntimeError("Version %s errored!" % (version.name))
    print("Datamined all versions.")
