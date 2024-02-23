import threading
import traceback

import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Downloader.VersionsParser as VersionsParser
import Utilities.Version as Version

import DataMiners.BehaviorPacks.BehaviorPacksDataMiners as BehaviorPacksDataMiners
import DataMiners.BlocksClient.BlocksClientDataMiners as BlocksClientDataMiners
import DataMiners.Credits.CreditsDataMiners as CreditsDataMiners
import DataMiners.DuplicateSounds.DuplicateSoundsDataMiners as DuplicateSoundsDataMiners
import DataMiners.Entities.EntitiesDataMiners as EntitiesDataMiners
import DataMiners.Items.ItemsDataMiners as ItemsDataMiners
import DataMiners.Languages.LanguagesDataMiners as LanguagesDataMiners
import DataMiners.LootTables.LootTablesDataMiners as LootTablesDataMiners
import DataMiners.MusicDefinitions.MusicDefinitionsDataMiners as MusicDefinitionsDataMiners
import DataMiners.NonExistentSounds.NonExistentSoundsDataMiners as NonExistentSoundsDataMiners
import DataMiners.Recipes.RecipesDataMiners as RecipesDataMiners
import DataMiners.ResourcePacks.ResourcePacksDataMiners as ResourcePacksDataMiners
import DataMiners.SoundDefinitions.SoundDefinitionsDataMiners as SoundDefinitionsDataMiners
import DataMiners.SoundFiles.SoundFilesDataMiners as SoundFilesDataMiners
import DataMiners.SoundsJson.SoundsJsonDataMiners as SoundsJsonDataMiners
import DataMiners.UndefinedSoundEvents.UndefinedSoundEventsDataMiners as UndefinedSoundEventsDataMiners
import DataMiners.UnusedSoundEvents.UnusedSoundEventsDataMiners as UnusedSoundEventsDataMiners

dataminers:list[DataMiner.DataMinerCollection] = [
    BehaviorPacksDataMiners.dataminers,
    BlocksClientDataMiners.dataminers,
    CreditsDataMiners.dataminers,
    DuplicateSoundsDataMiners.dataminers,
    EntitiesDataMiners.dataminers,
    ItemsDataMiners.dataminers,
    LanguagesDataMiners.dataminers,
    LootTablesDataMiners.dataminers,
    MusicDefinitionsDataMiners.dataminers,
    NonExistentSoundsDataMiners.dataminers,
    RecipesDataMiners.dataminers,
    ResourcePacksDataMiners.dataminers,
    SoundDefinitionsDataMiners.dataminers,
    SoundFilesDataMiners.dataminers,
    SoundsJsonDataMiners.dataminers,
    UndefinedSoundEventsDataMiners.dataminers,
    UnusedSoundEventsDataMiners.dataminers,
]

def run_with_dependencies(version:Version.Version, name:str, recalculate_this:bool=False, recalculate_everything:bool=False) -> None:
    data:DataMinerTyping.DependenciesTypedDict = {}
    dataminers_dict = {dataminer.name: dataminer.get_version(version) for dataminer in dataminers}
    locks = {dataminer.name: threading.Lock() for dataminer in dataminers}
    if detect_cycle(name, dataminers_dict, []):
        raise RuntimeError("Dataminer \"%s\" for \"%s\" has a dependency cycle!" % (dataminers_dict[name], version))
    __run_with_dependencies_child(data, locks, name, dataminers_dict, recalculate_this, recalculate_everything, dataminers_dict[name])
    exceptions:dict[str,Exception] = {}
    for dependency, datum in data.items():
        if isinstance(datum, Exception):
            exceptions[dependency] = datum
    if len(exceptions) > 0:
        for dependency, error in exceptions.items():
            print("File \"%s\" from \"%s\" errored!" % (name, version.name))
            traceback.print_exception(error)
        raise RuntimeError("Running dataminer \"%s\" on \"%s\" failed." % (name, version.name))

def detect_cycle(name:str, dataminers_dict:dict[str,DataMiner.DataMiner], already_found:list[str]) -> bool:
    '''Returns True if there is a cycle in the DataMiner's dependencies.'''
    if name not in dataminers_dict:
        raise KeyError("DataMiner \"%s\" does not exist!" % name)
    dependencies = dataminers_dict[name].dependencies
    for dependency in dependencies:
        if dependency not in dataminers_dict:
            raise KeyError("DataMiner \"%s\" lists non-existent DataMiner \"%s\" as a dependency!" % (dataminers_dict[name], dependency))
        this_already_found = already_found.copy()
        if dependency in this_already_found:
            return True
        this_already_found.append(dependency)
        if detect_cycle(dependency, dataminers_dict, this_already_found):
            return True
    else:
        return False

def __run_with_dependencies_child(data:DataMinerTyping.DependenciesTypedDict, locks:dict[str,threading.Lock], name:str, dataminers_dict:dict[str,DataMiner.DataMiner], recalculate:bool, recalculate_everything:bool, parent:DataMiner.DataMiner) -> None:
    lock = locks[name]
    with lock:
        if name in data:
            if isinstance(data[name], Exception):
                # don't need to do anything with this exception because data[name] is already an exception.
                raise RuntimeError("Another copy of DataMiner \"%s\" errored!" % name)
            else:
                pass # Return values do not do anything; this function just needs to end to complete.
        try:
            dataminer = dataminers_dict[name]

            if isinstance(dataminer, DataMiner.NullDataMiner):
                return # If it is a null dataminer, then there is nothing else to do.

            if not recalculate and dataminer.get_data_file_path().exists(): # get the data file if it already exists.
                data[name] = dataminer.get_data_file()
                return # Return so it doesn't try to datamine the data file anyways.

            # Dependencies (if none, then nothing will happen)
            threads:list[threading.Thread] = []
            for dependency in dataminer.dependencies:
                if dependency not in dataminers_dict: # I've been misspelling existent the whole time
                    raise KeyError("DataMiner \"%s\" lists non-existent DataMiner \"%s\" as a dependency!" % (dataminer, dependency))
                if isinstance(dataminers_dict[dependency], DataMiner.NullDataMiner):
                    raise RuntimeError("DataMiner \"%s\" on Version \"%s\" references a NullDataMiner for \"%s\"!" % (name, dataminer.version.name, dependency))
                thread = threading.Thread(target=__run_with_dependencies_child, args=[data, locks, dependency, dataminers_dict, recalculate_everything, recalculate_everything, parent])
                thread.start()
                threads.append(thread)
            for thread in threads: # wait for all child threads
                thread.join()

            for dependency in dataminer.dependencies:
                if dependency not in data:
                    raise KeyError("DataMiner \"%s\" failed to create child process of \"%s\"!" % (name, dependency))
                if isinstance(data[dependency], Exception):
                    raise RuntimeError("DataMiner \"%s\" cannot run because \"%s\" has raised an exception!" % (name, dependency))
            data[name] = dataminer.store(data, dataminers)
        except Exception as e:
            data[name] = e

def test_comparers() -> None:
    for dataminer in dataminers:
        print("%s:" % (dataminer.name))
        print(dataminer.comparer.get())
    print("All comparers successfully parsed.")

def user_interface() -> None:
    version_names = VersionsParser.versions_dict.get()
    version = None
    while version not in version_names:
        version = input("What version will be datamined? ")
    version = version_names[version]

    dataminer_names = {dataminer.name: dataminer for dataminer in dataminers}
    dataminer_collection = None
    while dataminer_collection not in dataminer_names and dataminer_collection != "*":
        dataminer_collection = input("What will be datamined (* for all)? %s " % str([dataminer.name for dataminer in dataminers]))
    if dataminer_collection == "*":
        dataminer_names = [dataminer.name for dataminer in dataminers]
    else:
        dataminer_names = [dataminer_collection]

    for dataminer_name in dataminer_names:
        run_with_dependencies(version, dataminer_name, recalculate_this=True, recalculate_everything=False)
        print("Successfully stored %s for %s." % (dataminer_name, version))
