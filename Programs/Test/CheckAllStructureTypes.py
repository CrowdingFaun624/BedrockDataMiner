import traceback

import Dataminer.AbstractDataminerCollection as AbstractDataminerCollection
import Domain.Domain as Domain
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.UserInput as UserInput
import Version.Version as Version


def check_types(version:Version.Version, dataminers:list[AbstractDataminerCollection.AbstractDataminerCollection]) -> None:
    environment = StructureEnvironment.PrinterEnvironment(StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.checking_all_types), None, version, 0)
    for dataminer_collection in dataminers:
        try:
            dataminer_collection.check_types(version, environment)
        except Exception as e:
            print(f"Failed on {dataminer_collection} on {version}")
            traceback.print_exception(e)
        dataminer_collection.clear_some_caches()

def check_all_structure_types(domain:Domain.Domain) -> None:
    selected_dataminers = UserInput.input_multi(domain.dataminer_collections, "dataminer", allow_select_all=True, show_options_first_time=True, close_enough=True)
    versions = domain.versions
    for version in versions.values():
        check_types(version, selected_dataminers)
    for dataminer_collection in selected_dataminers:
        dataminer_collection.clear_caches()
