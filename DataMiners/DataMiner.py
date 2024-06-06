import json
import traceback
from typing import (IO, Any, Callable, Literal, Mapping, NoReturn,
                    Sequence, TypeVar, overload)

from pathlib2 import Path

import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import Downloader.Accessor as Accessor
import Structure.DataPath as DataPath
import Structure.Normalizer as Normalizer
import Structure.StructureBase as StructureBase
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.CustomJson as CustomJson
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Version.Version as Version
import Version.VersionParser as VersionParser
import Version.VersionRange as VersionRange

EMPTY_FILE = "EMPTY_FILE" # for use in DataMiner.read_files

def str_to_version(version_str:str|None) -> Version.Version|None:
    if version_str is None: return None
    versions = VersionParser.versions
    output = versions.get(version_str)
    if output is None:
        raise Exceptions.UnrecognizedVersionError(version_str)
    return output

class DataMinerSettings():

    def __init__(self, start_version_str:str|None, end_version_str:str|None, dataminer_class:type["DataMiner"], name:str, files:list[str], dependencies:list[str]|None, kwargs:dict[str,Any]) -> None:

        self.version_range = VersionRange.VersionRange(str_to_version(start_version_str), str_to_version(end_version_str))
        self.file_name:str|None = None
        self.name:str|None = name
        self.structure:StructureBase.StructureBase|None = None
        self.dataminer_class = dataminer_class
        self.files = files
        self.dependencies = dependencies if dependencies is not None else []
        self.kwargs = kwargs

    def get_name(self) -> str:
        '''
        Get the name of this DataMinerSettings, and raise an exception if it is None.
        '''
        if self.name is None:
            raise Exceptions.AttributeNoneError("name", self)
        return self.name

    def get_file_name(self) -> str:
        '''
        Get the file name of this DataMinerSettings, and raise an exception if it is None.
        '''
        if self.file_name is None:
            raise Exceptions.AttributeNoneError("file_name", self)
        return self.file_name

    def __repr__(self) -> str:
        if self.name is None:
            return "<DataMinerSettings \"%s\"–\"%s\">" % (str(self.version_range.start), str(self.version_range.stop))
        else:
            return "<DataMinerSettings %s \"%s\"–\"%s\">" % (self.name, str(self.version_range.start), str(self.version_range.stop))

class DataMiner():

    parameters:TypeVerifier.TypeVerifier|None = None

    def __init__(self, version:Version.Version, settings:DataMinerSettings) -> None:
        self.version = version
        self.settings = settings
        self.file_name = self.settings.get_file_name()
        self.name = self.settings.get_name()
        self.files = set(self.settings.files)
        self.dependencies = self.settings.dependencies
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

    def store(self, environment:DataMinerEnvironment.DataMinerEnvironment, dataminer_collections:list["DataMinerCollection"]) -> Any:
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

    def store(self, environment:DataMinerEnvironment.DataMinerEnvironment, dataminer_collections:list["DataMinerCollection"]) -> NoReturn:
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

class DataMinerCollection():

    def __init__(self, file_name:str, name:str, structure:StructureBase.StructureBase, dataminers:list[DataMinerSettings]) -> None:
        self.dataminer_settings = dataminers
        self.name = name
        self.structure = structure
        self.file_name = file_name
        for dataminer in dataminers:
            dataminer.file_name = self.file_name
            dataminer.name = self.name
            dataminer.structure = self.structure

    def get_data_file(self, version:Version.Version, non_exist_ok:bool=False) -> Any:
        '''Opens the data file if it exists, and raises an error if it doesn't, or returns None if `non_exist_ok` is True'''
        data_path = FileManager.get_version_data_path(version.get_version_directory(), self.file_name)
        if not data_path.exists():
            if non_exist_ok:
                return None
            else:
                raise Exceptions.MissingDataFileError(self, self.file_name, version)
        with open(data_path, "rt") as f:
            return json.load(f, cls=CustomJson.decoder)

    def remove_data_file(self, version:Version.Version) -> None:
        data_path = FileManager.get_version_data_path(version.get_version_directory(), self.file_name)
        if data_path.exists():
            data_path.unlink()

    def has_tag(self, tag:str) -> bool:
        '''
        Returns True if the given tag could potentially be in this Version.
        :tag: The tag to test for.
        '''
        return self.structure.has_tag(tag)

    def get_tag_paths(self, version:Version.Version, tag:str, normalizer_dependencies:Normalizer.NormalizerDependencies, environment:StructureEnvironment.StructureEnvironment) -> list[DataPath.DataPath]:
        if not self.structure.has_tag(tag):
            return []
        dataminer = self.get_version(version)
        if isinstance(dataminer, NullDataMiner):
            return []
        data = dataminer.get_data_file()
        return self.structure.get_tag_paths(data, tag, version, normalizer_dependencies, environment)

    def compare(
            self,
            version1:Version.Version|None,
            version2:Version.Version,
            versions_between:list[Version.Version],
            normalizer_dependencies:Normalizer.NormalizerDependencies,
            environment:StructureEnvironment.StructureEnvironment,
            *,
            store:bool=True,
        ) -> str:
        '''Stores the comparison generated by this DataMinerCollection's Structure between two Versions, and returns the report.
        `data_cache` stores the output of `get_data_file`.'''
        if version1 is None:
            version2_data = self.get_data_file(version2)
            version1_data = type(version2_data)() # create new empty object.
        else:
            version1_data = self.get_data_file(version1)
            version2_data = self.get_data_file(version2)
        report, had_changes = self.structure.comparison_report(version1_data, version2_data, version1, version2, versions_between, normalizer_dependencies, environment)
        if store and had_changes:
            self.structure.store(report, self.name)
        return report

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return "<DataMinerCollection %s>" % self.name

    def clear_caches(self) -> None:
        '''Clears all caches of this DataMinerCollection's Structure.'''
        self.structure.clear_caches()

    def get_null_dataminer_settings(self) -> DataMinerSettings:
        '''Returns an instance of DataMinerSettings that is usable on a NullDataMiner.'''
        output = DataMinerSettings(None, None, NullDataMiner, self.name, [], [], {})
        output.file_name = self.file_name
        output.name = self.name
        output.structure = self.structure
        return output

    def get_dataminer_settings(self, version:Version.Version) -> DataMinerSettings:
        '''Returns a DataMinerSettings such that `version` is in the dataminer's VersionRange'''
        for dataminer_setting in self.dataminer_settings:
            if version in dataminer_setting.version_range:
                return dataminer_setting
        else: return self.get_null_dataminer_settings()

    def get_version(self, version:Version.Version) -> DataMiner:
        '''Returns a DataMiner such that `version` is in the dataminer's VersionRange.'''
        for dataminer_setting in self.dataminer_settings:
            if version in dataminer_setting.version_range:
                return dataminer_setting.dataminer_class(version, dataminer_setting)
        else: return NullDataMiner(version, self.get_null_dataminer_settings())

    def supports_version(self, version:Version.Version, all_dataminers:dict[str,"DataMinerCollection"]) -> bool:
        version_dataminer_settings:DataMinerSettings
        for dataminer_settings in self.dataminer_settings:
            if version in dataminer_settings.version_range:
                version_dataminer_settings = dataminer_settings
                break
        else: return False
        for version_file in version_dataminer_settings.files:
            if len(version.version_files[version_file].accessors) == 0:
                return False # cannot datamine it if its files are inaccessible
        else:
            return all(all_dataminers[dependency].supports_version(version, all_dataminers) for dependency in version_dataminer_settings.dependencies)

    def get_data_file_path(self, version:Version.Version) -> Path:
        return FileManager.get_version_data_path(version.get_version_directory(), self.file_name)
