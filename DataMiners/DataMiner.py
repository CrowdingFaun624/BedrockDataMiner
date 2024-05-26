import json
import traceback
from typing import (IO, Any, Callable, Iterable, Literal, Mapping, Sequence,
                    TypeVar, overload)

from pathlib2 import Path

import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.DataMinerTyping as DataMinerTyping
import Downloader.InstallManager as InstallManager
import Structure.DataPath as DataPath
import Structure.Normalizer as Normalizer
import Structure.StructureBase as StructureBase
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.CustomJson as CustomJson
import Utilities.FileManager as FileManager
import Utilities.TypeVerifier as TypeVerifier
import Version.Version as Version
import Version.VersionParser as VersionParser
import Version.VersionRange as VersionRange

EMPTY_FILE = "EMPTY_FILE" # for use in DataMiner.read_files

def str_to_version(version_str:str|None) -> Version.Version|None:
    if version_str is None: return None
    versions = VersionParser.versions
    output = versions.get(version_str)
    if output is None:
        raise KeyError("Version \"%s\" does not exist!" % version_str)
    return output

class DataMinerSettings():

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("start_version_str", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("end_version_str", "a str", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("dataminer_class", "a type", True, type),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("dependencies", "a list or None", True, TypeVerifier.UnionTypeVerifier(
            "a list or None",
            type(None),
            TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"),
        ))
    )

    def __init__(self, start_version_str:str|None, end_version_str:str|None, dataminer_class:type["DataMiner"], name:str, files:list[str], dependencies:list[str]|None, kwargs:dict[str,Any]) -> None:
        self.type_verifier.base_verify({"start_version_str": start_version_str, "end_version_str": end_version_str, "dataminer_class": dataminer_class, "name": name, "dependencies": dependencies})

        self.version_range = VersionRange.VersionRange(str_to_version(start_version_str), str_to_version(end_version_str))
        self.file_name:str|None = None
        self.name:str|None = name
        self.structure:StructureBase.StructureBase|None = None
        self.dataminer_class = dataminer_class
        self.files = files
        self.dependencies = dependencies if dependencies is not None else []
        self.kwargs = kwargs

    def __repr__(self) -> str:
        if self.name is None:
            return "<DataMinerSettings \"%s\"–\"%s\">" % (str(self.version_range.start), str(self.version_range.stop))
        else:
            return "<DataMinerSettings %s \"%s\"–\"%s\">" % (self.name, str(self.version_range.start), str(self.version_range.stop))

class DataMiner():

    parameters:DataMinerParameters.Parameters|None = None

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("version", "a Version", True, Version.Version),
        TypeVerifier.TypedDictKeyTypeVerifier("settings", "a DataMinerSettings", True, DataMinerSettings),
    )

    def __init__(self, version:Version.Version, settings:DataMinerSettings) -> None:
        self.type_verifier.base_verify({"version": version, "settings": settings})

        self.version = version
        self.settings = settings
        self.file_name = self.settings.file_name
        self.name = self.settings.name
        self.files = set(self.settings.files)
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

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        '''Makes the dataminer get the file. Returns the output.'''
        raise NotImplementedError("`activate` was called by %s without being defined by a subclass." % repr(self))

    def get_data_file_path(self) -> Path:
        if self.version.version_folder is None:
            raise FileNotFoundError("Version \"%s\"'s version folder does not exist!" % self.version.name)
        return FileManager.get_version_data_path(self.version.version_folder, self.file_name)

    def store(self, environment:DataMinerEnvironment.DataMinerEnvironment, dataminer_collections:list["DataMinerCollection"]) -> Any:
        '''Makes the dataminer get the file. Returns the output and stores it in a file.'''
        data = self.activate(environment)
        if data is None:
            raise RuntimeError("DataMiner %s returned None!" % self)
        if self.version.version_folder is None:
            raise FileNotFoundError("Version \"%s\"'s version folder does not exist!" % self.version.name)
        data_path = FileManager.get_version_data_path(self.version.version_folder, None)
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

    def get_accessor(self, file_type:str) -> InstallManager.InstallManager:
        if file_type not in self.files:
            raise RuntimeError("Attempted to get accessor of file type \"%s\" from %s; this dataminer only has permission to take files from [%s]!" % (file_type, self, ", ".join(sorted(self.files))))
        return self.version.get_accessor(file_type)

    def get_files_in(self, accessor:InstallManager.InstallManager, parent:str) -> Iterable[str]:
        return accessor.get_files_in(parent)

    def get_file_list(self, accessor:InstallManager.InstallManager) -> list[str]:
        return accessor.get_file_list()

    @overload
    def read_file(self, accessor:InstallManager.InstallManager, file_name:str, mode:Literal["b"]) -> bytes: ...
    @overload
    def read_file(self, accessor:InstallManager.InstallManager, file_name:str, mode:Literal["t"]) -> str: ...
    @overload
    def read_file(self, accessor:InstallManager.InstallManager, file_name:str) -> str: ...
    def read_file(self, accessor:InstallManager.InstallManager, file_name:str, mode:Literal["b", "t"]="t") -> str|bytes:
        return accessor.read(file_name, mode)

    read_files_typevar = TypeVar("read_files_typevar")

    def _read_file(self, accessor:InstallManager.InstallManager, file_name:str, mode:Literal["b", "t"], callable:None|Callable[[IO],read_files_typevar], non_exist_ok:bool) -> str|bytes|Any:
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
    def read_files(self, accessor:InstallManager.InstallManager, files:Sequence[str], non_exist_ok:bool=False) -> dict[str,str]: ...
    @overload
    def read_files(self, accessor:InstallManager.InstallManager, files:Sequence[tuple[str,Literal["t"],None]], non_exist_ok:bool=False) -> dict[str,str]: ...
    @overload
    def read_files(self, accessor:InstallManager.InstallManager, files:Sequence[tuple[str,Literal["b"],None]], non_exist_ok:bool=False) -> dict[str,bytes]: ...
    @overload
    def read_files(self, accessor:InstallManager.InstallManager, files:Sequence[tuple[str,Literal["t"],Callable[[IO[str]],read_files_typevar]]], non_exist_ok:bool=False) -> dict[str,read_files_typevar]: ...
    @overload
    def read_files(self, accessor:InstallManager.InstallManager, files:Sequence[tuple[str,Literal["b"],Callable[[IO[bytes]],read_files_typevar]]], non_exist_ok:bool=False) -> dict[str,read_files_typevar]: ...
    @overload
    def read_files(self, accessor:InstallManager.InstallManager, files:Sequence[str|tuple[str,Literal["b", "t"],None|Callable[[IO],read_files_typevar]]], non_exist_ok:bool=False) -> Mapping[str,str|bytes|read_files_typevar]: ...
    def read_files(self, accessor:InstallManager.InstallManager, files:Sequence[str|tuple[str,Literal["b", "t"],None|Callable[[IO],read_files_typevar]]], non_exist_ok:bool=False) -> Mapping[str,str|bytes|read_files_typevar]:
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
            raise RuntimeError("Failed to read files!")

        return file_results

    def file_exists(self, accessor:InstallManager.InstallManager, file_name:str) -> bool:
        return accessor.file_exists(file_name)

    def get_file(self, accessor:InstallManager.InstallManager, file_name:str, mode:Literal["b","t"]="t") -> FileManager.FilePromise:
        return accessor.get_file(file_name, mode)

class NullDataMiner(DataMiner):
    '''Returned when a dataminer collection has no dataminer for a data type.'''

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict, structure_environment:StructureEnvironment.StructureEnvironment) -> Any:
        raise RuntimeError("Attempted to use `activate` from a NullDataMiner!")

    def store(self, dependency_data:DataMinerTyping.DependenciesTypedDict, dataminer_collections:list["DataMinerCollection"]) -> Any:
        raise RuntimeError("Attempted to use `store` from a NullDataMiner!")

    def get_file_list(self) -> Iterable[str]:
        raise RuntimeError("Attempted to use `get_file_list` from a NullDataMiner!")

    def get_accessor(self, file_type:str) -> InstallManager.InstallManager:
        raise RuntimeError("Attempted to use `get_accessor` from a NullDataMiner!")

    def get_files_in(self, accessor:InstallManager.InstallManager, parent:str) -> Iterable[str]:
        raise RuntimeError("Attempted to use `get_files_in` from a NullDataMiner!")

    def read_file(self, file_name: str, mode: Literal["b","t"] = "t") -> str | bytes:
        raise RuntimeError("Attempted to use `read_file` from a NullDataMiner!")

    def read_files(self, files:list[str|tuple[str,str,Callable[[IO],Any]|None]]) -> dict[str,str|bytes|Any]:
        raise RuntimeError("Attempted to use `read_files` from a NullDataMiner!")

    def file_exists(self, accessor:InstallManager.InstallManager, file_name:str) -> bool:
        raise RuntimeError("Attempted to use `file_exists` from a NullDataMiner!")

    def get_file(self, file_name:str, mode:Literal["b","t"]="t") -> FileManager.FilePromise:
        raise RuntimeError("Attempted to use `get_file` from a NullDataMiner!")

class DataMinerCollection():

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("file_name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("structure", "a StructureBase", True, StructureBase.StructureBase),
        TypeVerifier.TypedDictKeyTypeVerifier("dataminers", "a list", True, TypeVerifier.ListTypeVerifier(DataMinerSettings, list, "a DataMinerSettings", "a list")),
    )

    def __init__(self, file_name:str, name:str, structure:StructureBase.StructureBase, dataminers:list[DataMinerSettings]) -> None:
        self.type_verifier.base_verify({"file_name": file_name, "name": name, "structure": structure, "dataminers": dataminers})

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
            return json.load(f, cls=CustomJson.decoder)

    def remove_data_file(self, version:Version.Version) -> None:
        if version.version_folder is None:
            raise FileNotFoundError("Version \"%s\"'s version folder does not exist!" % version.name)
        data_path = FileManager.get_version_data_path(version.version_folder, self.file_name)
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
        return DataMinerSettings(None, None, NullDataMiner, self.name, [], [], {})

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
        if version.version_folder is None:
            raise FileNotFoundError("Version \"%s\"'s version folder does not exist!" % version.name)
        return FileManager.get_version_data_path(version.version_folder, self.file_name)
