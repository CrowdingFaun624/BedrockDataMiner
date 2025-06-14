import traceback

import Dataminer.Dataminers as Dataminers
import Domain.Domain as Domain
from Structure.StructureEnvironment import EnvironmentType, StructureEnvironment
from Utilities.Exceptions import DataminersFailureError
from Version.Version import Version


def datamine_version(version:Version, domain:Domain.Domain, print_messages:bool=True) -> None:
    dataminers = Dataminers.get_dataminable_dataminers(version, domain)
    already_files = set(Dataminers.currently_has_data_files_from(version, domain))
    needed_files = [dataminer for dataminer in dataminers if dataminer not in already_files]
    if len(needed_files) == 0:
        if print_messages:
            print(f"Skipped \"{version.name}\" due to already being complete.")
        # All of this Version's data files are already there.
    else:
        if print_messages:
            print(f"Started \"{version.name}\".")
        structure_environment = StructureEnvironment(EnvironmentType.all_datamining, domain)
        failure_dataminers = Dataminers.run(version, needed_files, structure_environment)
        if len(failure_dataminers) > 0:
            for failed_dataminer, exception in failure_dataminers:
                print(f"\nFailed to datamine \"{failed_dataminer.name}\" for \"{version.name}\":")
                if exception is not None:
                    traceback.print_exception(exception)
            print()
            raise DataminersFailureError(version, [dataminer_tuple[0] for dataminer_tuple in failure_dataminers])
    if not version.latest:
        for version_file in version.version_files:
            for accessor in version_file.accessors:
                accessor.all_done() # remove all of the installed client files from the version directory so I don't have to clog my storage

def main(domain:Domain.Domain) -> None:
    dataminers_dict = domain.dataminer_collections
    for version in reversed(domain.versions.values()):
        if not any(dataminer_collection.supports_version(version) for dataminer_collection in dataminers_dict.values()):
            print(f"Skipped \"{version.name}\" due to being unarchived.")
        else:
            datamine_version(version, domain)
        version.close_accessors()
    print("Datamined all versions.")
