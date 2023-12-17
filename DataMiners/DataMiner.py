import json
from pathlib2 import Path
import time
import threading
import traceback
from typing import Any, Callable, IO, Iterable, Literal

import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.FileManager as FileManager
import Utilities.Version as Version
import Utilities.VersionRange as VersionRange

EMPTY_FILE = "EMPTY_FILE" # for use in DataMiner.read_files

class DataMinerSettings():
    def __init__(self, start_version:Version.Version|Literal["-"], end_version:Version.Version|Literal["-"], dataminer_class:type["DataMiner"], dependencies:list[str]|None=None, **kwargs) -> None:
        if start_version != "-" and not isinstance(start_version, Version.Version):
            raise TypeError("`start_version` is not a Version or Literal[\"-\"]!")
        if end_version != "-" and not isinstance(end_version, Version.Version):
            raise TypeError("`end_version` is not a Version or Literal[\"-\"]!")
        if not isinstance(dataminer_class, type):
            raise TypeError("`dataminer_class` is not a type!")
        if dependencies is not None and not isinstance(dependencies, list):
            raise TypeError("`dependencies` is not None or a list!")
        if dependencies is not None and not all(isinstance(dependency, str) for dependency in dependencies):
            raise TypeError("An item in `dependencies` is not a str!")

        self.version_range = VersionRange.VersionRange(start_version, end_version)
        self.file_name:str = None
        self.name:str = None
        self.dataminer_class = dataminer_class
        self.dependencies = dependencies if dependencies is not None else []
        self.kwargs = kwargs
    
    def __repr__(self) -> str:
        if self.name is None:
            return "<DataMinerSettings \"%s\"–\"%s\">" % (str(self.version_range.start), str(self.version_range.stop))
        else:
            return "<DataMinerSettings %s \"%s\"–\"%s\">" % (self.name, str(self.version_range.start), str(self.version_range.stop))

class DataMiner():
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
        
    def __repr__(self) -> str:
        return "<%s %s on %s>" % (self.__class__.__name__, self.name, self.version.name)

    def initialize(self, **kwargs) -> None:
        '''`DataMinerSettings.__init__(**kwargs)` -> `DataMiner.initialize(**kwargs)`.'''
        if len(kwargs) > 0:
            raise NotImplementedError("`initialize` was called with non-empty parameters without being defined by a subclass.")
    
    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict|None=None) -> Any:
        '''Makes the dataminer get the file. Returns the output.'''
        raise NotImplementedError("`activate` was called without being defined by a subclass.")

    def get_data_file_path(self) -> Path:
        return FileManager.get_version_data_path(self.version.version_folder, self.file_name)

    def store(self, dependency_data:DataMinerTyping.DependenciesTypedDict|None=None) -> Any:
        '''Makes the dataminer get the file. Returns the output and stores it in a file.'''
        data = self.activate(dependency_data)
        if data is None:
            raise RuntimeError("DataMiner %s returned None!" % self)
        data_path = FileManager.get_version_data_path(self.version.version_folder, None)
        if not data_path.exists():
            data_path.mkdir()
        with open(self.get_data_file_path(), "wt") as f:
            json.dump(data, f)
        return data
    
    def get_data_file(self) -> Any:
        with open(self.get_data_file_path(), "rt") as f:
            return json.load(f)

    def get_file_list(self) -> Iterable[str]:
        return self.version.install_manager.get_file_list()

    def read_file(self, file_name:str, mode:str="t") -> str|bytes:
        return self.version.install_manager.read(file_name, mode)
    
    def read_files(self, files:list[str|tuple[str,str,None|Callable[[IO],Any]]], non_exist_ok:bool=False) -> dict[str,str|bytes|Any]:
        '''Asynchronously obtains a list of files. Items of the list can be a filename string or (filename string, mode, optional_callable).
        The optional callable takes in an IO object and returns a transformed value.'''
        def read_async(file_name:str, mode:str, callable:Callable[[IO],Any]|None, file_results:dict[str,str|bytes|Any], non_exist_ok:bool) -> str:
            try:
                if not non_exist_ok or self.file_exists(file_name):
                    if callable is None:
                        file_results[file_name] = self.read_file(file_name, mode)
                    else:
                        with self.get_file(file_name, mode) as f:
                            file_results[file_name] = callable(f)
                else:
                    file_results[file_name] = EMPTY_FILE
            except Exception as e:
                file_results[file_name] = e
        DEFAULT_MODE = "t"
        files = [(file, DEFAULT_MODE, None) if isinstance(file, str) else file for file in files]
        file_names = [file[0] for file in files]
        if any(count >= 2 for count in (file_names.count(file_name) for file_name in file_names)): # duplicate item tester
            duplicate_files = [file for file in file_names if file_names.count(file) >= 2]
            raise ValueError("Duplicated files: %s" % str(duplicate_files))
        file_results:dict[str,str|bytes|Any] = {}
        for file_name, mode, callable in files:
            file_results[file_name] = None
            thread = threading.Thread(target=read_async, args=[file_name, mode, callable, file_results, non_exist_ok])
            thread.start()
        while True:
            time.sleep(0.05)
            exceptions:dict[str,Exception] = {}
            all_complete = True
            for file_name, file_result in file_results.items():
                if isinstance(file_result, Exception):
                    exceptions[file_name] = file_result
                    all_complete = False
                if file_result is None:
                    all_complete = False
            if len(exceptions) > 0:
                for file_name, exception in exceptions.items():
                    print("File \"%s\" from \"%s\" errored!" % (file_name, self.version.name))
                    traceback.print_exception(exception)
                raise RuntimeError("File fetching failed.")
            if all_complete:
                break
        for file_name, file_result in file_results.items(): # sets files that don't exist to None.
            if file_result is EMPTY_FILE:
                file_results[file_name] = None
        return file_results

    def file_exists(self, file_name:str) -> bool:
        return self.version.install_manager.file_exists(file_name)

    def get_file(self, file_name:str, mode:str="t") -> IO:
        return self.version.install_manager.get_file(file_name, mode)

class NullDataMiner(DataMiner):
    '''Returned when a dataminer collection has no dataminer for a data type.'''
    def get_file(self, file_name:str, mode:str="t") -> IO:
        raise RuntimeError("Attempted to use `get_file` from a NullDataMiner!")
    def activate(self) -> Any:
        raise RuntimeError("Attempted to use `activate` from a NullDataMiner!")
    def store(self) -> Any:
        raise RuntimeError("Attempted to use `store` from a NullDataMiner!")
    def get_file_list(self) -> Iterable[str]:
        raise RuntimeError("Attempted to use `get_file_list` from a NullDataMiner!")
    def read_file(self, file_name: str, mode: str = "t") -> str | bytes:
        raise RuntimeError("Attempted to use `read_file` from a NullDataMiner!")
    def read_files(self, files:list[str|tuple[str,str,Callable[[IO],Any]|None]]) -> dict[str,str|bytes|Any]:
        raise RuntimeError("Attempted to use `read_files` from a NullDataMiner!")

class DataMinerCollection():
    def __init__(self, file_name:str, name:str, dataminers:list[DataMinerSettings]) -> None:
        if not isinstance(file_name, str):
            raise TypeError("`file_name` is not a str!")
        if not isinstance(name, str):
            raise TypeError("`name` is not a str!")
        if not isinstance(dataminers, list):
            raise TypeError("`dataminers` is not a list!")
        if not all(isinstance(setting, DataMinerSettings) for setting in dataminers):
            raise TypeError("An item of `dataminers` is not a DataMinerSettings!")
        
        self.dataminer_settings = dataminers
        self.name = name
        self.file_name = file_name
        for dataminer in dataminers:
            dataminer.file_name = self.file_name
            dataminer.name = self.name
    
    def __repr__(self) -> str:
        return "<DataMinerCollection %s>" % self.name
    
    def get_version(self, version:Version.Version) -> DataMiner:
        '''Returns a DataMiner such that `version` is in the dataminer's VersionRange.'''
        for dataminer_setting in self.dataminer_settings:
            if version in dataminer_setting.version_range:
                return dataminer_setting.dataminer_class(version, dataminer_setting)
        else: return NullDataMiner(version, dataminer_setting)
