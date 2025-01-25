import traceback
from typing import Iterable, Sequence

import Dataminer.AbstractDataminerCollection as AbstractDataminerCollection
import Dataminer.DataminerEnvironment as DataminerEnvironment
import Domain.Domain as Domain
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.UserInput as UserInput
import Version.Version as Version


def get_dataminable_dataminers(version:Version.Version, domain:Domain.Domain) -> Iterable[AbstractDataminerCollection.AbstractDataminerCollection]:
    '''
    Returns the names of all data files that this Version supports.
    :version: The version to test.
    '''
    return (dataminer for dataminer in domain.dataminer_collections.values() if dataminer.supports_version(version))

def currently_has_data_files_from(version:Version.Version, domain:Domain.Domain) -> Iterable[AbstractDataminerCollection.AbstractDataminerCollection]:
    return (dataminer for dataminer in domain.dataminer_collections.values() if dataminer.get_data_file_path(version).exists())

def get_dataminer_order(version:Version.Version, unordered_dataminers:Sequence[AbstractDataminerCollection.AbstractDataminerCollection]) -> list[AbstractDataminerCollection.AbstractDataminerCollection]:
    '''
    Sorts the dataminers such that they can be completed in order. Does not change the original list.
    :unordered_dataminers: The unordered list of DataminerCollections to sort.
    '''
    ordered_dataminers:list[AbstractDataminerCollection.AbstractDataminerCollection] = []
    already_added:set[AbstractDataminerCollection.AbstractDataminerCollection] = set()
    for dataminer in unordered_dataminers:
        if dataminer not in already_added:
            resolve_dataminer_order(ordered_dataminers, already_added, dataminer, version)
    return ordered_dataminers

def resolve_dataminer_order(
    dataminers:list[AbstractDataminerCollection.AbstractDataminerCollection],
    already_added:set[AbstractDataminerCollection.AbstractDataminerCollection],
    current_dataminer:AbstractDataminerCollection.AbstractDataminerCollection,
    version:Version.Version
) -> None:
    for dependency in current_dataminer.get_dependencies(version):
        if dependency not in already_added:
            resolve_dataminer_order(dataminers, already_added, dependency, version)
    dataminers.append(current_dataminer)
    already_added.add(current_dataminer)

def run(
        version:Version.Version,
        dataminer_collections:Sequence[AbstractDataminerCollection.AbstractDataminerCollection],
        structure_environment:StructureEnvironment.StructureEnvironment,
        *,
        recalculate_everything:bool=False,
        print_messages:bool=False
    ) -> list[tuple[AbstractDataminerCollection.AbstractDataminerCollection, Exception|None]]:
    '''
    Runs and stores the output of multiple Dataminers. Returns the DataminerCollections that it failed to datamine and the corresponding exception.
    :version: The Version to run the Dataminers on.
    :dataminer_collections: The list of DataminerCollections to use for datamining.
    :structure_environment: The StructureEnvironment to use when checking types.
    :all_dataminers: Every DataminerCollection.
    :recalculate_everything: If True, forces all dependencies to be recalculated.
    :print_messages: If True, messages will be printed after each Dataminer finishes.
    '''
    for dataminer in dataminer_collections:
        dataminer.remove_data_file(version)
    dataminer_order = get_dataminer_order(version, dataminer_collections)
    dataminer_environment = DataminerEnvironment.DataminerEnvironment(DataminerEnvironment.DataminerDependencies({}), structure_environment)
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
    failure_dataminers:list[tuple[AbstractDataminerCollection.AbstractDataminerCollection, Exception|None]] = []
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
        structure_environment = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.all_datamining, domain)
    else:
        structure_environment = StructureEnvironment.StructureEnvironment(StructureEnvironment.EnvironmentType.datamining, domain)
    recalculate_everything = False # if all dependencies should be recalculated too
    cannot_datamine:list[Version.Version] = []
    for version in versions:
        filtered_dataminers = [dataminer for dataminer in dataminer_collections if dataminer.supports_version(version)]
        failure_dataminers = run(version, filtered_dataminers, structure_environment, recalculate_everything=recalculate_everything, print_messages=True)
        if len(failure_dataminers) > 0:
            cannot_datamine.append(version)
    if len(versions) > 1:
        print(f"Failed to datamine {len(cannot_datamine)} versions:\n{", ".join(version.name for version in cannot_datamine)}")
