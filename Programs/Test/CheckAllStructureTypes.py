import traceback

import Component.Importer as Importer
import DataMiner.DataMinerCollection as DataMinerCollection
import DataMiner.DataMiners as DataMiners
import Programs.CompareAll as CompareAll
import Structure.StructureEnvironment as StructureEnvironment
import Version.Version as Version


def check_types(version:Version.Version, dataminers:list[DataMinerCollection.DataMinerCollection]) -> None:
    environment = StructureEnvironment.PrinterEnvironment(StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.checking_all_types), None, version, 0)
    for dataminer_collection in dataminers:
        try:
            dataminer_collection.check_types(version, environment)
        except Exception as e:
            print("Failed on %r on %r" % (dataminer_collection, version))
            traceback.print_exception(e)
        dataminer_collection.clear_some_caches()

def check_all_structure_types() -> None:
    dataminers = DataMiners.dataminers
    selected_dataminers = CompareAll.select_dataminers(dataminers)
    versions = Importer.versions
    for version in versions.values():
        check_types(version, selected_dataminers)
    for dataminer_collection in selected_dataminers:
        dataminer_collection.clear_caches()
