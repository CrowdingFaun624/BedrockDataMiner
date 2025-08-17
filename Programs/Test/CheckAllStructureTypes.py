import traceback

import Domain.Domain as Domain
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Structure.StructureEnvironment import (
    EnvironmentType,
    PrinterEnvironment,
    StructureEnvironment,
)
from Utilities.MemoryUsage import memory_usage
from Utilities.UserInput import input_multi
from Version.Version import Version


def check_types(version:Version, dataminers:list[AbstractDataminerCollection], domain:"Domain.Domain") -> None:
    structure_environment = StructureEnvironment(EnvironmentType.checking_all_types, domain)
    for dataminer_collection in dataminers:
        environment = PrinterEnvironment(structure_environment, dataminer_collection.get_structure_info(version), version, 0)
        try:
            dataminer_collection.check_types(version, environment)
        except Exception as e:
            print(f"Failed on {dataminer_collection} on {version}")
            traceback.print_exception(e)
        dataminer_collection.clear_old_caches({(version, environment.structure_info)})
        memory_usage.adjust()

def check_all_structure_types(domain:Domain.Domain) -> None:
    selected_dataminers = input_multi(domain.dataminer_collections, "dataminer", allow_select_all=True, show_options_first_time=True, close_enough=True)
    versions = domain.versions
    for version in versions.values():
        check_types(version, selected_dataminers, domain)
        version.close_accessors()
    for dataminer_collection in selected_dataminers:
        dataminer_collection.clear_all_caches()
    memory_usage.reset()
