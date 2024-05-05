import traceback

import DataMiners.DataMiners as DataMiners
import Version.VersionParser as VersionParser
import Version.Version as Version

def datamine_version(version:Version.Version, dataminer_names:list[str], print_messages:bool=True) -> bool:
    supported_files = set(DataMiners.dataminable_files(version))
    already_files = set(DataMiners.currently_has_data_files_from(version))
    if len(supported_files - already_files) == 0:
        if print_messages:
            print("Skipped \"%s\" due to already being complete." % (version.name))
        return True # All of this Version's data files are already there.
    if print_messages:
        print("Started \"%s\"." % (version.name))
    for dataminer_name in dataminer_names:
        try:
            DataMiners.run_with_dependencies(version, dataminer_name)
        except Exception as e:
            print("Version \"%s\" errored!" % version.name)
            traceback.print_exception(e)
            return False
    if version.install_manager is not None and not version.latest:
        version.install_manager.all_done() # remove all of the installed client files from the version folder so I don't have to clog my storage
    return True

def main() -> None:
    dataminer_names = [dataminer_collection.name for dataminer_collection in DataMiners.dataminers]
    for version in reversed(VersionParser.versions.values()):
        if version.download_method is Version.DownloadMethod.DOWNLOAD_NONE:
            print("Skipped \"%s\" due to being unarchived." % (version.name))
        else:
            all_dataminers_success = datamine_version(version, dataminer_names)
            if not all_dataminers_success:
                raise RuntimeError("Version %s errored!" % (version.name))
    print("Datamined all versions.")
