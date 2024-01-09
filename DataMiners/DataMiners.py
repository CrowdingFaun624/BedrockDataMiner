import threading
import traceback

import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.Version as Version

import DataMiners.Blocks.BlocksDataMiners as BlocksDataMiners
import DataMiners.ResourcePacks.ResourcePacksDataMiners as ResourcePacksDataMiners
import DataMiners.SoundDefinitions.SoundDefinitionsDataMiners as SoundDefinitionsDataMiners
import DataMiners.SoundFiles.SoundFilesDataMiners as SoundFilesDataMiners
import DataMiners.SoundsJson.SoundsJsonDataMiners as SoundsJsonDataMiners

dataminers:list[DataMiner.DataMinerCollection] = [
    BlocksDataMiners.dataminers,
    ResourcePacksDataMiners.dataminers,
    SoundDefinitionsDataMiners.dataminers,
    SoundFilesDataMiners.dataminers,
    SoundsJsonDataMiners.dataminers,
]

def run_with_dependencies(version:Version.Version, name:str, recalculate:bool=False) -> None:
    data:DataMinerTyping.DependenciesTypedDict = {}
    dataminers_dict = {dataminer.name: dataminer.get_version(version) for dataminer in dataminers}
    if detect_cycle(name, dataminers_dict, []):
        raise RuntimeError("Dataminer \"%s\" for \"%s\" has a dependency cycle!" % (dataminers_dict[name], version))
    return_data = __run_with_dependencies_child(data, name, dataminers_dict, recalculate, dataminers_dict[name])
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

def __run_with_dependencies_child(data:DataMinerTyping.DependenciesTypedDict, name:str, dataminers_dict:dict[str,DataMiner.DataMiner], recalculate:bool, parent:DataMiner.DataMiner) -> None:
    if name in data:
        if isinstance(data[name], Exception):
            # don't need to do anything with this exception because data[name] is already an exception.
            raise RuntimeError("Another copy of DataMiner \"%s\" errored!" % name)
        else:
            return data[name]
    try:
        dataminer = dataminers_dict[name]
        if not recalculate and dataminer.get_data_file_path().exists(): # get the data file if it already exists.
            return_data = dataminer.get_data_file()
            return return_data
        
        # Dependencies (if none, then nothing will happen)
        threads:list[threading.Thread] = []
        for dependency in dataminer.dependencies:
            if dependency not in dataminers_dict: # I've been misspelling existent the whole time
                raise KeyError("DataMiner \"%s\" lists non-existent DataMiner \"%s\" as a dependency!" % (dataminer, dependency))
            thread = threading.Thread(target=__run_with_dependencies_child, args=[data, dependency, dataminers_dict, recalculate, parent])
            thread.start()
            threads.append(thread)
        for thread in threads: # wait for all child threads
            thread.join()

        if isinstance(dataminer, DataMiner.NullDataMiner):
            raise RuntimeError("DataMiner \"%s\" references a NullDataMiner!" % parent)
        for dependency in dataminer.dependencies:
            if isinstance(data[dependency], Exception):
                raise RuntimeError("DataMiner \"%s\" cannot run because \"%s\" has raised an exception!" % (name, dependency))
        return_data = dataminer.store(data)
        data[name] = return_data
        return return_data
    except Exception as e:
        data[name] = e

def user_interface() -> None:
    import Downloader.VersionsParser as VersionsParser

    versions = VersionsParser.parse()
    version_names = {version.name: version for version in versions}
    version = None
    while version not in version_names:
        version = input("What version will be datamined? ")
    version = version_names[version]

    dataminer_names = {dataminer.name: dataminer for dataminer in dataminers}
    dataminer_collection = None
    while dataminer_collection not in dataminer_names or dataminer_collection == "*":
        dataminer_collection = input("What will be datamined (* for all)? %s " % str([dataminer.name for dataminer in dataminers]))
    if dataminer_collection == "*":
        dataminer_names = [dataminer.name for dataminer in dataminers]
    else:
        dataminer_names = [dataminer_collection]

    for dataminer_name in dataminer_names:
        run_with_dependencies(version, dataminer_name, True)
        print("Successfully stored %s for %s." % (dataminer_name, version))
