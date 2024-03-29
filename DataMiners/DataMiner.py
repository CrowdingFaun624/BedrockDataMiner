import copy
import json
from pathlib2 import Path
import threading
import traceback
from typing import Any, Callable, IO, Iterable, Literal, Sequence

import Comparison.Comparer as Comparer
import Comparison.Normalizer as Normalizer
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.DataMinerParameters as DataMinerParameters
import Downloader.VersionsParser as VersionsParser
import Utilities.FileManager as FileManager
from Utilities.FunctionCaller import WaitValue
import Utilities.Version as Version
import Utilities.VersionRange as VersionRange

EMPTY_FILE = "EMPTY_FILE" # for use in DataMiner.read_files

def str_to_version(version_str:str|None) -> Version.Version|Literal["-"]:
    if version_str is None: return "-"
    if version_str == "-": raise RuntimeError("Version range \"-\" is not supported!")
    else:
        versions_dict = VersionsParser.versions_dict.get()
        if version_str in versions_dict:
            return versions_dict[version_str]
        else:
            raise KeyError("Version \"%s\" does not exist!" % version_str)

class DataMinerSettings():

    def __init__(self, start_version_str:str|None, end_version_str:str|None, dataminer_class:type["DataMiner"], dependencies:list[str]|None=None, **kwargs) -> None:
        if not (start_version_str is None or isinstance(start_version_str, str)):
            raise TypeError("`start_version_str` is not a str or None, but instead \"%s\"!" % start_version_str)
        if not (end_version_str is None or isinstance(end_version_str, str)):
            raise TypeError("`end_version_str` is not a str or None, but instead \"%s\"!" % end_version_str)
        if not isinstance(dataminer_class, type):
            raise TypeError("`dataminer_class` is not a type!")
        if dependencies is not None and not isinstance(dependencies, list):
            raise TypeError("`dependencies` is not None or a list!")
        if dependencies is not None and not all(isinstance(dependency, str) for dependency in dependencies):
            raise TypeError("An item in `dependencies` is not a str!")

        self.version_range = VersionRange.VersionRange(str_to_version(start_version_str), str_to_version(end_version_str))
        self.file_name:str|None = None
        self.name:str|None = None
        self.comparer:WaitValue[Comparer.Comparer]|None = None
        self.dataminer_class = dataminer_class
        self.dependencies = dependencies if dependencies is not None else []
        self.kwargs = kwargs

    def __repr__(self) -> str:
        if self.name is None:
            return "<DataMinerSettings \"%s\"–\"%s\">" % (str(self.version_range.start), str(self.version_range.stop))
        else:
            return "<DataMinerSettings %s \"%s\"–\"%s\">" % (self.name, str(self.version_range.start), str(self.version_range.stop))

class DataMiner():

    parameters:DataMinerParameters.Parameters|None = None

    def __init__(self, version:Version.Version, settings:DataMinerSettings) -> None:
        if not isinstance(version, Version.Version):
            raise TypeError("`version` is not a Version!")
        if not isinstance(settings, DataMinerSettings):
            raise TypeError("`settings` is not a DataMinerSettings!")

        self.version = version
        self.settings = settings
        self.file_name = self.settings.file_name
        self.name = self.settings.name
        self.dependencies = self.settings.dependencies
        if not isinstance(self, NullDataMiner) and self.version not in self.settings.version_range:
            raise ValueError("Version \"%s\" is not a valid version for this dataminer!" % self.version.name)

        self.initialize(**settings.kwargs)

    def __repr__(self) -> str:
        return "<%s %s on %s>" % (self.__class__.__name__, self.name, self.version.name)

    def initialize(self, **kwargs) -> None:
        '''`DataMinerSettings.__init__(**kwargs)` -> `DataMiner.initialize(**kwargs)`.'''
        if len(kwargs) > 0:
            raise NotImplementedError("`initialize` was called with %i non-empty parameters by %s without being defined by a subclass:\n%s" % (len(kwargs), repr(self), kwargs))

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> Any:
        '''Makes the dataminer get the file. Returns the output.'''
        raise NotImplementedError("`activate` was called by %s without being defined by a subclass." % repr(self))

    def get_data_file_path(self) -> Path:
        if self.version.version_folder is None:
            raise FileNotFoundError("Version \"%s\"'s version folder does not exist!" % self.version.name)
        return FileManager.get_version_data_path(self.version.version_folder, self.file_name)

    def store(self, dependency_data:DataMinerTyping.DependenciesTypedDict, dataminer_collections:list["DataMinerCollection"]) -> Any:
        '''Makes the dataminer get the file. Returns the output and stores it in a file.'''
        data = self.activate(dependency_data)
        if data is None:
            raise RuntimeError("DataMiner %s returned None!" % self)
        if self.version.version_folder is None:
            raise FileNotFoundError("Version \"%s\"'s version folder does not exist!" % self.version.name)
        data_path = FileManager.get_version_data_path(self.version.version_folder, None)
        if not data_path.exists():
            data_path.mkdir()
        with open(self.get_data_file_path(), "wt") as f:
            json.dump(data, f)

        normalizer_dependencies = Normalizer.LocalNormalizerDependencies(Normalizer.NormalizerDependencies({}, dataminer_collections), self.version, None)
        if self.settings.comparer is not None:
            normalized_data = self.settings.comparer.get().normalize(copy.deepcopy(data), normalizer_dependencies)
            self.settings.comparer.get().check_types(normalized_data)

        return data

    def get_data_file(self) -> Any:
        with open(self.get_data_file_path(), "rt") as f:
            return json.load(f)

    def get_files_in(self, parent:str) -> Iterable[str]:
        if self.version.install_manager is None:
            raise RuntimeError("Attempted to call `get_files_in` on version (\"%s\") with no download available!" % self.version.name)
        return self.version.install_manager.get_files_in(parent)

    def get_file_list(self) -> Iterable[str]:
        if self.version.install_manager is None:
            raise RuntimeError("Attempted to call `get_file_list` on version (\"%s\") with no download available!" % self.version.name)
        return self.version.install_manager.get_file_list()

    def read_file(self, file_name:str, mode:str="t") -> str|bytes:
        if self.version.install_manager is None:
            raise RuntimeError("Attempted to call `read_file` on version (\"%s\") with no download available!" % self.version.name)
        return self.version.install_manager.read(file_name, mode)

    def read_files(self, files:Sequence[str|tuple[str,Literal["t", "b"],None|Callable[[IO],Any]]], non_exist_ok:bool=False) -> dict[str,str|bytes|Any]:
        '''Asynchronously obtains a list of files. Items of the list can be a filename string or (filename string, mode, optional_callable).
        The optional callable takes in an IO object and returns a transformed value.'''

        def read_async(files:Iterable[tuple[str,str,None|Callable[[IO],Any]]], file_results:dict[str,str|bytes|Any], non_exist_ok:bool, lock:threading.Lock) -> None:
            with lock:
                for file_name, mode, callable in files:
                    try:
                        if not non_exist_ok or self.file_exists(file_name):
                            if callable is None:
                                file_results[file_name] = self.read_file(file_name, mode)
                            else:
                                file = self.get_file(file_name, mode)
                                with file.open() as f:
                                    file_results[file_name] = callable(f)
                                file.all_done()
                        else: # file does not exist
                            file_results[file_name] = EMPTY_FILE
                    except Exception as e:
                        e.args = tuple(list(e.args) + ["Failed to get file \"%s\"!" % (file_name)])
                        file_results[file_name] = e
                        return

        if self.version.install_manager is None:
            raise RuntimeError("Attempted to call `read_files` on version (\"%s\") with no download available!" % self.version.name)

        DEFAULT_MODE = "t"
        LIMIT = 16 # how many threads can be created.
        normalized_files:list[tuple[str,str,None|Callable[[IO],Any]]] = [(file, DEFAULT_MODE, None) if isinstance(file, str) else file for file in files]
        file_names = [file[0] for file in normalized_files]

        if any(count >= 2 for count in (file_names.count(file_name) for file_name in file_names)): # duplicate item tester
            duplicate_files = [file for file in file_names if file_names.count(file) >= 2]
            raise ValueError("Duplicated files: %s" % str(duplicate_files))

        thread_count = len(normalized_files) if len(normalized_files) < LIMIT else LIMIT
        thread_responsibilities:list[list[tuple[str,str,None|Callable[[IO],Any]]]] = [[] for index in range(thread_count)] # keeps track of what each thread will do.
        file_results:dict[str,str|bytes|Any] = {}
        for index, (file_name, mode, callable) in enumerate(normalized_files):
            file_results[file_name] = None
            thread_responsibilities[index % thread_count].append((file_name, mode, callable))

        locks = [threading.Lock() for index in range(LIMIT)]
        for lock, thread_responsibility in zip(locks, thread_responsibilities):
            thread = threading.Thread(target=read_async, args=[thread_responsibility, file_results, non_exist_ok, lock])
            thread.start()
        for lock in locks:
            lock.acquire() # wait for every thread to finish

        exceptions:dict[str,Exception|None] = {} # Exception if the thread had an exception; None if the file returned None (should not happen)
        all_complete = True
        for file_name, file_result in file_results.items():
            if file_result is None or isinstance(file_result, Exception):
                exceptions[file_name] = file_result
                all_complete = False
        for file_name, exception in exceptions.items():
            print("File \"%s\" from \"%s\" errored!" % (file_name, self.version.name))
            if exception is None:
                print("File \"%s\" returned None! This should not happen!" % file_name)
            else:
                traceback.print_exception(exception)
        if not all_complete:
            raise RuntimeError("File fetching failed due to Exception or incompletion.")

        for file_name, file_result in file_results.items(): # sets files that don't exist to None.
            if file_result is EMPTY_FILE:
                file_results[file_name] = None
        return file_results

    def file_exists(self, file_name:str) -> bool:
        if self.version.install_manager is None:
            raise RuntimeError("Attempted to call `file_exists` on version (\"%s\") with no download available!" % self.version.name)
        return self.version.install_manager.file_exists(file_name)

    def get_file(self, file_name:str, mode:str="t") -> FileManager.FilePromise:
        if self.version.install_manager is None:
            raise RuntimeError("Attempted to call `get_file` on version (\"%s\") with no download available!" % self.version.name)
        return self.version.install_manager.get_file(file_name, mode)

class NullDataMiner(DataMiner):
    '''Returned when a dataminer collection has no dataminer for a data type.'''

    def get_file(self, file_name:str, mode:str="t") -> FileManager.FilePromise:
        raise RuntimeError("Attempted to use `get_file` from a NullDataMiner!")

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> Any:
        raise RuntimeError("Attempted to use `activate` from a NullDataMiner!")

    def store(self, dependency_data:DataMinerTyping.DependenciesTypedDict, dataminer_collections:list["DataMinerCollection"]) -> Any:
        raise RuntimeError("Attempted to use `store` from a NullDataMiner!")

    def get_file_list(self) -> Iterable[str]:
        raise RuntimeError("Attempted to use `get_file_list` from a NullDataMiner!")

    def read_file(self, file_name: str, mode: str = "t") -> str | bytes:
        raise RuntimeError("Attempted to use `read_file` from a NullDataMiner!")

    def read_files(self, files:list[str|tuple[str,str,Callable[[IO],Any]|None]]) -> dict[str,str|bytes|Any]:
        raise RuntimeError("Attempted to use `read_files` from a NullDataMiner!")


class DataMinerCollection():
    def __init__(self, file_name:str, name:str, comparer:WaitValue[Comparer.Comparer]|Comparer.Comparer, dataminers:list[DataMinerSettings]) -> None:
        if not isinstance(file_name, str):
            raise TypeError("`file_name` is not a str!")
        if not isinstance(name, str):
            raise TypeError("`name` is not a str!")
        if not isinstance(comparer, (Comparer.Comparer, WaitValue)):
            raise TypeError("`comparer` is not a Comparer or WaitValue!")
        if not isinstance(dataminers, list):
            raise TypeError("`dataminers` is not a list!")
        if not all(isinstance(setting, DataMinerSettings) for setting in dataminers):
            raise TypeError("An item of `dataminers` is not a DataMinerSettings!")

        self.dataminer_settings = dataminers
        self.name = name
        self.comparer = comparer if isinstance(comparer, WaitValue) else WaitValue(lambda: comparer)
        self.file_name = file_name
        for dataminer in dataminers:
            dataminer.file_name = self.file_name
            dataminer.name = self.name
            dataminer.comparer = self.comparer

    def get_data_file(self, version:Version.Version, non_exist_ok:bool=False) -> Any:
        '''Opens the data file if it exists, and raises an error if it doesn't, or returns None if `non_exist_ok` is True'''
        if version is None:
            raise TypeError("Attempted to get the data file of None!")
        if version.version_folder is None:
            raise FileNotFoundError("Version \"%s\"'s version folder does not exist!" % version.name)
        data_path = FileManager.get_version_data_path(version.version_folder, self.file_name)
        if not data_path.exists():
            if non_exist_ok:
                return None
            else:
                raise FileNotFoundError("Version \"%s\" does not currently have a data file \"%s\"!" % (version.name, self.file_name))
        with open(data_path, "rt") as f:
            return json.load(f)

    def compare(
            self,
            version1:Version.Version|None,
            version2:Version.Version,
            versions_between:list[Version.Version],
            normalizer_dependencies:Normalizer.NormalizerDependencies,
            store:bool=True,
        ) -> str:
        '''Stores the comparison generated by this DataMinerCollection's Comparer between two Versions, and returns the report.
        `data_cache` stores the output of `get_data_file`.'''
        if version1 is None:
            version2_data = self.get_data_file(version2)
            version1_data = type(version2_data)() # create new empty object.
        else:
            version1_data = self.get_data_file(version1)
            version2_data = self.get_data_file(version2)
        report, had_changes = self.comparer.get().comparison_report(version1_data, version2_data, version1, version2, versions_between, normalizer_dependencies)
        if store and had_changes:
            self.comparer.get().store(report)
        return report

    def __repr__(self) -> str:
        return "<DataMinerCollection %s>" % self.name

    def get_null_dataminer_settings(self) -> DataMinerSettings:
        '''Returns an instance of DataMinerSettings that is usable on a NullDataMiner.'''
        return DataMinerSettings(None, None, NullDataMiner)

    def get_version(self, version:Version.Version) -> DataMiner:
        '''Returns a DataMiner such that `version` is in the dataminer's VersionRange.'''
        for dataminer_setting in self.dataminer_settings:
            if version in dataminer_setting.version_range:
                return dataminer_setting.dataminer_class(version, dataminer_setting)
        else: return NullDataMiner(version, self.get_null_dataminer_settings())
