import traceback

import Component.Importer as Importer
import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import Structure.StructureEnvironment as StructureEnvironment
import Version.Version as Version
import Version.VersionParser as VersionParser

dataminers = list(Importer.dataminer_collections.values())

SINGLE_VERSION_ENVIRONMENT = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.datamining)
MANY_VERSION_ENVIRONMENT = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.all_datamining)

def get_dataminable_dataminers(version:Version.Version, all_dataminers:dict[str,DataMiner.DataMinerCollection]) -> list[DataMiner.DataMinerCollection]:
    '''
    Returns the names of all data files that this Version supports.
    :version: The version to test.
    :all_dataminers: A dict of all DataMinerCollections.
    '''
    output = [dataminer for dataminer in dataminers if dataminer.supports_version(version, all_dataminers)]
    return output

def currently_has_data_files_from(version:Version.Version) -> list[DataMiner.DataMinerCollection]:
    return [dataminer for dataminer in dataminers if dataminer.get_data_file_path(version).exists()]

def get_dataminer_order(version:Version.Version, unordered_dataminers:list[DataMiner.DataMinerCollection]) -> list[DataMiner.DataMinerCollection]:
    '''
    Sorts the dataminers such that they can be completed in order. Does not change the original list.
    :unordered_dataminers: The unordered list of DataMinerCollections to sort.
    '''
    ordered_dataminers:list[DataMiner.DataMinerCollection] = []
    already_added:set[DataMiner.DataMinerCollection] = set()
    for dataminer in unordered_dataminers:
        if dataminer not in already_added:
            resolve_dataminer_order(ordered_dataminers, already_added, dataminer, version)
    return ordered_dataminers

def resolve_dataminer_order(dataminers:list[DataMiner.DataMinerCollection], already_added:set[DataMiner.DataMinerCollection], current_dataminer:DataMiner.DataMinerCollection, version:Version.Version) -> None:
    for dependency in current_dataminer.get_version(version).dependencies:
        if dependency not in already_added:
            resolve_dataminer_order(dataminers, already_added, dependency, version)
    dataminers.append(current_dataminer)
    already_added.add(current_dataminer)

def run(
        version:Version.Version,
        dataminer_collections:list[DataMiner.DataMinerCollection],
        structure_environment:StructureEnvironment.StructureEnvironment,
        all_dataminers:dict[str,DataMiner.DataMinerCollection],
        *,
        recalculate_everything:bool=False,
        print_messages:bool=False
    ) -> list[tuple[DataMiner.DataMinerCollection, Exception]]:
    '''
    Runs and stores the output of multiple DataMiners. Returns the DataMinerCollections that it failed to datamine and the corresponding exception.
    :version: The Version to run the DataMiners on.
    :dataminer_collections: The list of DataMinerCollections to use for datamining.
    :structure_environment: The StructureEnvironment to use when checking types.
    :all_dataminers: Every DataMinerCollection.
    :recalculate_everything: If True, forces all dependencies to be recalculated.
    :print_messages: If True, messages will be printed after each DataMiner finishes.
    '''
    dataminers_list = list(all_dataminers.values())
    for dataminer in dataminer_collections:
        dataminer.remove_data_file(version)
    dataminer_order = get_dataminer_order(version, dataminer_collections)
    dataminer_environment = DataMinerEnvironment.DataMinerEnvironment(DataMinerEnvironment.DataMinerDependencies({}), structure_environment)
    if recalculate_everything:
        for dataminer in dataminer_order:
            dataminer.remove_data_file(version)
    else:
        # remove dataminers that are already stored if recalculate everything is False
        i = 0 
        while i < len(dataminer_order):
            if dataminer_order[i].get_data_file_path(version).exists():
                dataminer_environment.dependency_data.set_item(dataminer_order[i].name, dataminer_order[i].get_data_file(version))
                del dataminer_order[i]
            else: i += 1
    failure_dataminers:list[tuple[DataMiner.DataMinerCollection, Exception]] = []
    failure_dataminers_set:set[str] = set()
    for dataminer_collection in dataminer_order:
        try:
            dataminer = dataminer_collection.get_version(version)
            for dependency in dataminer.dependencies:
                if dependency in failure_dataminers_set:
                    continue # no use trying to datamine this if any of its dependencies excepted.
            dataminer_output = dataminer.store(dataminer_environment, dataminers_list)
            dataminer_environment.dependency_data.set_item(dataminer_collection.name, dataminer_output)
        except Exception as e:
            failure_dataminers_set.add(dataminer_collection.name)
            failure_dataminers.append((dataminer_collection, e))
            if print_messages:
                traceback.print_exception(e)
                print("Failed to store %s for %s." % (dataminer_collection.name, version))
        else:
            if print_messages:
                print("Successfully stored %s for %s." % (dataminer.name, version))
    return failure_dataminers

def test_structures() -> None:
    for dataminer in dataminers:
        print("%s:" % (dataminer.name))
        print(dataminer.structure)
    print("All structures successfully parsed.")

def user_interface() -> None:
    version_names = VersionParser.versions
    all_dataminers_dict = {dataminer.name: dataminer for dataminer in dataminers}
    version = None
    while version not in version_names and version != "*":
        version = input("What version will be datamined? ")
    if version == "*":
        versions = list(version_names.values())
        dataminable_file_names = sorted(dataminer.name for dataminer in dataminers)
        dataminable_dataminers_set = set(dataminers)
    else:
        versions = [version_names[version]]
        dataminable_dataminers_set:set[DataMiner.DataMinerCollection] = set()
        for version in versions:
            dataminable_dataminers_set.update(get_dataminable_dataminers(version, all_dataminers_dict))
        dataminable_file_names = sorted(dataminer.name for dataminer in dataminable_dataminers_set)

    dataminer_collection = None
    while dataminer_collection not in dataminable_file_names and dataminer_collection != "*":
        dataminer_collection = input("What will be datamined (* for all)? %s " % (dataminable_file_names))
    if dataminer_collection == "*":
        dataminers_to_datamine = [dataminer for dataminer in dataminers if dataminer in dataminable_dataminers_set]
    else:
        dataminers_to_datamine = [dataminer for dataminer in dataminers if dataminer.name == dataminer_collection]


    if len(versions) > 1:
        structure_environment = MANY_VERSION_ENVIRONMENT
    else:
        structure_environment = SINGLE_VERSION_ENVIRONMENT
    recalculate_everything = False # if all dependencies should be recalculated too
    cannot_datamine:list[Version.Version] = []
    for version in versions:
        if len(version.version_files) == 0: continue
        failure_dataminers = run(version, dataminers_to_datamine, structure_environment, all_dataminers_dict, recalculate_everything=recalculate_everything, print_messages=True)
        if len(failure_dataminers) > 0:
            cannot_datamine.append(version)
    if len(versions) > 1:
        print("Failed to datamine %i versions:\n%s")
