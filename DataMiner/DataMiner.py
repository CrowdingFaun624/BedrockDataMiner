import json
import traceback
from typing import (IO, TYPE_CHECKING, Any, Callable, Literal, Mapping,
                    NoReturn, Sequence, TypeVar, overload)

from pathlib2 import Path

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerSettings as DataMinerSettings
import Downloader.Accessor as Accessor
import Structure.Normalizer as Normalizer
import Utilities.CustomJson as CustomJson
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Version.Version as Version

if TYPE_CHECKING:
    import DataMiner.DataMinerCollection as DataMinerCollection

EMPTY_FILE = "EMPTY_FILE" # for use in DataMiner.read_files

class DataMiner():

    parameters:TypeVerifier.TypeVerifier|None = None

    def __init__(self, version:Version.Version, settings:DataMinerSettings.DataMinerSettings) -> None:
        self.version = version
        self.settings = settings
        self.file_name = self.settings.get_file_name()
        self.name = self.settings.get_name()
        self.files = set(self.settings.files)
        self.dependencies = self.settings.get_dependencies()
        self.dependencies_str = [dependency.name for dependency in self.dependencies]
        if not isinstance(self, NullDataMiner) and self.version not in self.settings.version_range:
            raise Exceptions.VersionOutOfRangeError(self.version, self.settings.version_range, "in DataMiner %r" % (self,))

        self.initialize(**settings.kwargs)

    def __repr__(self) -> str:
        return "<%s %s on %s>" % (self.__class__.__name__, self.name, self.version.name)

    def initialize(self, **kwargs) -> None:
        '''`DataMinerSettings.__init__(**kwargs)` -> `DataMiner.initialize(**kwargs)`.'''
        if len(kwargs) > 0:
            raise Exceptions.DataMinerKeywordArgumentsExistError(kwargs, self)

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        '''Makes the dataminer get the file. Returns the output.'''
        raise Exceptions.DataMinerLacksActivateError(self)

    def get_data_file_path(self) -> Path:
        return FileManager.get_version_data_path(self.version.get_version_directory(), self.file_name)

    def store(self, environment:DataMinerEnvironment.DataMinerEnvironment, dataminer_collections:list["DataMinerCollection.DataMinerCollection"]) -> Any:
        '''Makes the dataminer get the file. Returns the output and stores it in a file.'''
        data = self.activate(environment)
        if data is None:
            raise Exceptions.DataMinerNullReturnError(self)
        data_path = FileManager.get_version_data_path(self.version.get_version_directory(), None)
        if not data_path.exists():
            data_path.mkdir()
        with open(self.get_data_file_path(), "wt") as f:
            json.dump(data, f, separators=(",", ":"), cls=CustomJson.encoder)

        normalizer_dependencies = Normalizer.LocalNormalizerDependencies(Normalizer.NormalizerDependencies({}, dataminer_collections), self.version, None)
        if self.settings.structure is not None:
            normalized_data = self.settings.structure.normalize(data, normalizer_dependencies, environment.structure_environment)
            self.settings.structure.check_types(normalized_data, environment.structure_environment)

        return self.get_data_file() # since the normalizing immediately before may modify it.

    def get_data_file(self) -> Any:
        with open(self.get_data_file_path(), "rt") as f:
            return json.load(f, cls=CustomJson.decoder)

    def get_accessor(self, file_type:str) -> Accessor.Accessor:
        if file_type not in self.files:
            raise Exceptions.DataMinerFileTypePermissionError(self, file_type, sorted(self.files))
        return self.version.get_accessor(file_type)

    def get_files_in(self, accessor:Accessor.Accessor, parent:str) -> list[str]:
        return accessor.get_files_in(parent)

    def get_file_list(self, accessor:Accessor.Accessor) -> list[str]:
        return accessor.get_file_list()

    @overload
    def read_file(self, accessor:Accessor.Accessor, file_name:str, mode:Literal["b"]) -> bytes: ...
    @overload
    def read_file(self, accessor:Accessor.Accessor, file_name:str, mode:Literal["t"]) -> str: ...
    @overload
    def read_file(self, accessor:Accessor.Accessor, file_name:str) -> str: ...
    def read_file(self, accessor:Accessor.Accessor, file_name:str, mode:Literal["b", "t"]="t") -> str|bytes:
        return accessor.read(file_name, mode)

    read_files_typevar = TypeVar("read_files_typevar")

    def _read_file(self, accessor:Accessor.Accessor, file_name:str, mode:Literal["b", "t"], callable:None|Callable[[IO],read_files_typevar], non_exist_ok:bool) -> str|bytes|Any:
        try:
            if not non_exist_ok or self.file_exists(accessor, file_name):
                if callable is None:
                    return self.read_file(accessor, file_name, mode)
                else:
                    file = self.get_file(accessor, file_name, mode)
                    with file.open() as f:
                        output = callable(f)
                    file.all_done()
                    return output
            else: # file does not exist
                return EMPTY_FILE
        except Exception as e:
            e.args = tuple(list(e.args) + ["Failed to get file \"%s\"!" % (file_name)])
            return e

    @overload
    def read_files(self, accessor:Accessor.Accessor, files:Sequence[str], non_exist_ok:bool=False) -> dict[str,str]: ...
    @overload
    def read_files(self, accessor:Accessor.Accessor, files:Sequence[tuple[str,Literal["t"],None]], non_exist_ok:bool=False) -> dict[str,str]: ...
    @overload
    def read_files(self, accessor:Accessor.Accessor, files:Sequence[tuple[str,Literal["b"],None]], non_exist_ok:bool=False) -> dict[str,bytes]: ...
    @overload
    def read_files(self, accessor:Accessor.Accessor, files:Sequence[tuple[str,Literal["t"],Callable[[IO[str]],read_files_typevar]]], non_exist_ok:bool=False) -> dict[str,read_files_typevar]: ...
    @overload
    def read_files(self, accessor:Accessor.Accessor, files:Sequence[tuple[str,Literal["b"],Callable[[IO[bytes]],read_files_typevar]]], non_exist_ok:bool=False) -> dict[str,read_files_typevar]: ...
    @overload
    def read_files(self, accessor:Accessor.Accessor, files:Sequence[str|tuple[str,Literal["b", "t"],None|Callable[[IO],read_files_typevar]]], non_exist_ok:bool=False) -> Mapping[str,str|bytes|read_files_typevar]: ...
    def read_files(self, accessor:Accessor.Accessor, files:Sequence[str|tuple[str,Literal["b", "t"],None|Callable[[IO],read_files_typevar]]], non_exist_ok:bool=False) -> Mapping[str,str|bytes|read_files_typevar]:
        '''Synchronously obtains a list of files. Items of the list can be a filename string or (filename string, mode, optional_callable).
        The optional callable takes in an IO object and returns a transformed value.'''

        DEFAULT_MODE = "t"
        normalized_files:list[tuple[str,Literal["b", "t"],None|Callable[[IO],Any]]] = [(file, DEFAULT_MODE, None) if isinstance(file, str) else file for file in files]

        exceptions:list[tuple[str, Exception]] = []
        file_results:dict[str,str|bytes|DataMiner.read_files_typevar] = {}
        for file_name, file_mode, callable in normalized_files:
            try:
                if not non_exist_ok or self.file_exists(accessor, file_name):
                    if callable is None:
                        file_result = self.read_file(accessor, file_name, file_mode)
                    else:
                        file = self.get_file(accessor, file_name, file_mode)
                        with file.open() as f:
                            file_result = callable(f)
                        file.all_done()
                    file_results[file_name] = file_result
                else: # file does not exist
                    pass
            except Exception as e:
                exceptions.append((file_name, e))

        for file_name, exception in exceptions:
            print("Failed to get file \"%s\"!" % file_name)
            traceback.print_exception(exception)
            print()
        if len(exceptions) > 0:
            raise Exceptions.DataMinerReadFilesError(self)

        return file_results

    def file_exists(self, accessor:Accessor.Accessor, file_name:str) -> bool:
        return accessor.file_exists(file_name)

    def get_file(self, accessor:Accessor.Accessor, file_name:str, mode:Literal["b","t"]="t") -> FileManager.FilePromise:
        return accessor.get_file(file_name, mode)

class NullDataMiner(DataMiner):
    '''Returned when a dataminer collection has no dataminer for a data type.'''

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> NoReturn:
        raise Exceptions.NullDataMinerMethodError(self, self.activate)

    def store(self, environment:DataMinerEnvironment.DataMinerEnvironment, dataminer_collections:list["DataMinerCollection.DataMinerCollection"]) -> NoReturn:
        raise Exceptions.NullDataMinerMethodError(self, self.store)

    def get_file_list(self) -> NoReturn:
        raise Exceptions.NullDataMinerMethodError(self, self.get_file_list)

    def get_accessor(self, file_type:str) -> NoReturn:
        raise Exceptions.NullDataMinerMethodError(self, self.get_accessor)

    def get_files_in(self, accessor:Accessor.Accessor, parent:str) -> NoReturn:
        raise Exceptions.NullDataMinerMethodError(self, self.get_files_in)

    def read_file(self, file_name: str, mode: Literal["b","t"] = "t") -> NoReturn:
        raise Exceptions.NullDataMinerMethodError(self, self.read_file)

    def read_files(self, files:list[str|tuple[str,str,Callable[[IO],Any]|None]]) -> NoReturn:
        raise Exceptions.NullDataMinerMethodError(self, self.read_files)

    def file_exists(self, accessor:Accessor.Accessor, file_name:str) -> NoReturn:
        raise Exceptions.NullDataMinerMethodError(self, self.file_exists)

    def get_file(self, file_name:str, mode:Literal["b","t"]="t") -> NoReturn:
        raise Exceptions.NullDataMinerMethodError(self, self.get_file)
