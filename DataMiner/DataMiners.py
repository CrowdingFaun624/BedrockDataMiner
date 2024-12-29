import traceback
from typing import Sequence

import DataMiner.AbstractDataMinerCollection as AbstractDataMinerCollection
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import Domain.Domain as Domain
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.UserInput as UserInput
import Version.Version as Version

SINGLE_VERSION_ENVIRONMENT = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.datamining)
MANY_VERSION_ENVIRONMENT = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.all_datamining)

def get_dataminable_dataminers(version:Version.Version, domain:Domain.Domain) -> list[AbstractDataMinerCollection.AbstractDataMinerCollection]:
    '''
    Returns the names of all data files that this Version supports.
    :version: The version to test.
    '''
    output = [dataminer for dataminer in domain.dataminer_collections.values() if dataminer.supports_version(version)]
    return output

def currently_has_data_files_from(version:Version.Version, domain:Domain.Domain) -> list[AbstractDataMinerCollection.AbstractDataMinerCollection]:
    return [dataminer for dataminer in domain.dataminer_collections.values() if dataminer.get_data_file_path(version).exists()]

def get_dataminer_order(version:Version.Version, unordered_dataminers:Sequence[AbstractDataMinerCollection.AbstractDataMinerCollection]) -> list[AbstractDataMinerCollection.AbstractDataMinerCollection]:
    '''
    Sorts the dataminers such that they can be completed in order. Does not change the original list.
    :unordered_dataminers: The unordered list of DataMinerCollections to sort.
    '''
    ordered_dataminers:list[AbstractDataMinerCollection.AbstractDataMinerCollection] = []
    already_added:set[AbstractDataMinerCollection.AbstractDataMinerCollection] = set()
    for dataminer in unordered_dataminers:
        if dataminer not in already_added:
            resolve_dataminer_order(ordered_dataminers, already_added, dataminer, version)
    return ordered_dataminers

def resolve_dataminer_order(
    dataminers:list[AbstractDataMinerCollection.AbstractDataMinerCollection],
    already_added:set[AbstractDataMinerCollection.AbstractDataMinerCollection],
    current_dataminer:AbstractDataMinerCollection.AbstractDataMinerCollection,
    version:Version.Version
) -> None:
    for dependency in current_dataminer.get_dependencies(version):
        if dependency not in already_added:
            resolve_dataminer_order(dataminers, already_added, dependency, version)
    dataminers.append(current_dataminer)
    already_added.add(current_dataminer)

def run(
        version:Version.Version,
        dataminer_collections:Sequence[AbstractDataMinerCollection.AbstractDataMinerCollection],
        structure_environment:StructureEnvironment.StructureEnvironment,
        *,
        recalculate_everything:bool=False,
        print_messages:bool=False
    ) -> list[tuple[AbstractDataMinerCollection.AbstractDataMinerCollection, Exception|None]]:
    '''
    Runs and stores the output of multiple DataMiners. Returns the DataMinerCollections that it failed to datamine and the corresponding exception.
    :version: The Version to run the DataMiners on.
    :dataminer_collections: The list of DataMinerCollections to use for datamining.
    :structure_environment: The StructureEnvironment to use when checking types.
    :all_dataminers: Every DataMinerCollection.
    :recalculate_everything: If True, forces all dependencies to be recalculated.
    :print_messages: If True, messages will be printed after each DataMiner finishes.
    '''
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
    failure_dataminers:list[tuple[AbstractDataMinerCollection.AbstractDataMinerCollection, Exception|None]] = []
    failure_dataminers_set:set[str] = set()
    for dataminer_collection in dataminer_order:
        try:
            if any(dependency.name in failure_dataminers_set for dependency in dataminer_collection.get_dependencies(version)):
                failure_dataminers_set.add(dataminer_collection.name)
                failure_dataminers.append((dataminer_collection, None))
                continue # no use trying to datamine this if any of its dependencies excepted.
            dataminer_output = dataminer_collection.store(version, dataminer_environment)
            dataminer_environment.dependency_data.set_item(dataminer_collection.name, dataminer_output)
        except Exception as e:
            failure_dataminers_set.add(dataminer_collection.name)
            failure_dataminers.append((dataminer_collection, e))
            if print_messages:
                traceback.print_exception(e)
                print(f"Failed to store {dataminer_collection.name} for {version}.")
        else:
            if print_messages:
                print(f"Successfully stored {dataminer_collection.name} for {version}.")
    if len(failure_dataminers) > 0 and print_messages:
        print(f"Failed to store dataminers: [{", ".join(dataminer[0].name for dataminer in failure_dataminers)}]")
    return failure_dataminers

def user_interface(domain:Domain.Domain) -> None:
    version_names = domain.versions
    versions = UserInput.input_multi(version_names, "version", allow_select_all=True)
    selectable_dataminer_collections = {
        dataminer_collection.name: dataminer_collection
        for dataminer_collection in domain.dataminer_collections.values()
        if any(dataminer_collection.supports_version(version) for version in versions)
    }
    dataminer_collections = UserInput.input_multi(selectable_dataminer_collections, "dataminer collection", allow_select_all=True, show_options_first_time=True, close_enough=True)

    if len(versions) > 1:
        structure_environment = MANY_VERSION_ENVIRONMENT
    else:
        structure_environment = SINGLE_VERSION_ENVIRONMENT
    recalculate_everything = False # if all dependencies should be recalculated too
    cannot_datamine:list[Version.Version] = []
    for version in versions:
        filtered_dataminers = [dataminer for dataminer in dataminer_collections if dataminer.supports_version(version)]
        failure_dataminers = run(version, filtered_dataminers, structure_environment, recalculate_everything=recalculate_everything, print_messages=True)
        if len(failure_dataminers) > 0:
            cannot_datamine.append(version)
    if len(versions) > 1:
        print(f"Failed to datamine {len(cannot_datamine)} versions:\n{", ".join(version.name for version in cannot_datamine)}")
