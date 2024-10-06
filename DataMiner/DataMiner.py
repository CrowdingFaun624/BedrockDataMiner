import json
from typing import TYPE_CHECKING, Any, NoReturn, TypeVar, overload

from pathlib2 import Path

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerSettings as DataMinerSettings
import Downloader.Accessor as Accessor
import Serializer.Serializer as Serializer
import Utilities.CustomJson as CustomJson
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.FileManager as FileManager
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Version.Version as Version

if TYPE_CHECKING:
    import DataMiner.DataMinerCollection as DataMinerCollection

a = TypeVar("a", bound=Accessor.Accessor)

class DataMiner():

    parameters:TypeVerifier.TypeVerifier|None = TypeVerifier.TypedDictTypeVerifier()
    '''TypeVerifier for verifying the json arguments of this DataMiner'''
    serializer_names:set[str] = set()
    '''The keys of Serializers given to this DataMiner's settings must match `serializer_names`.'''

    def __init__(self, version:Version.Version, settings:DataMinerSettings.DataMinerSettings) -> None:
        self.version = version
        self.settings = settings
        self.file_name = self.settings.get_file_name()
        self.name = self.settings.get_name()
        self.serializers = self.settings.serializers
        self.files = set(self.settings.get_version_file_types())
        self.files_str = {version_file_type.name for version_file_type in self.files}
        self.dependencies = self.settings.get_dependencies()
        self.dependencies_str = [dependency.name for dependency in self.dependencies]
        if not isinstance(self, NullDataMiner) and self.version not in self.settings.get_version_range():
            raise Exceptions.VersionOutOfRangeError(self.version, self.settings.version_range, "in DataMiner %r" % (self,))

        self.initialize(**settings.arguments)

    def __repr__(self) -> str:
        return "<%s %s on %s>" % (self.__class__.__name__, self.name, self.version.name)

    @classmethod
    def manipulate_arguments(cls, arguments:dict[str,Any]) -> None:
        '''Manipulates the arguments of this DataMiner before they are passed into `initialize`.'''
        return None

    def initialize(self, **kwargs) -> None:
        '''`DataMinerSettings.__init__(**kwargs)` -> `DataMiner.initialize(**kwargs)`.'''
        pass

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

        if self.settings.structure is not None:
            normalized_data = self.settings.structure.normalize(data, environment.get_printer_environment(self.version))
            self.settings.structure.check_types(normalized_data, environment.structure_environment, (self.version,))

        return self.get_data_file() # since the normalizing immediately before may modify it.

    def get_data_file(self) -> Any:
        with open(self.get_data_file_path(), "rt") as f:
            return json.load(f, cls=CustomJson.decoder)

    def get_accessor(self, file_type:str, accessor_type:type[a]=Accessor.Accessor) -> a:
        if file_type not in self.files_str:
            raise Exceptions.DataMinerFileTypePermissionError(self, file_type, sorted(self.files_str))
        accessor = self.version.get_accessor(file_type, accessor_type)
        if accessor is None:
            raise Exceptions.DataMinerAccessorWrongTypeError(self, file_type, accessor_type)
        return accessor

    def get_serializer(self, serializer_key:str) -> Serializer.Serializer:
        if self.serializers is None:
            raise Exceptions.AttributeNoneError("serializers", self)
        serializer = self.serializers.get(serializer_key)
        if serializer is None:
            raise Exceptions.DataMinerUnrecognizedSerializerError(self, serializer_key)
        return serializer

    def export_file(self, file_bytes:bytes, file_name:str, serializer_key:str="main") -> File.File|Any:
        serializer = self.get_serializer(serializer_key)
        if serializer.store_as_file_default:
            return File.new_file(file_bytes, file_name, serializer)
        else:
            try:
                return serializer.deserialize(file_bytes)
            except Exception:
                raise Exceptions.SerializationFailureError(serializer, file_name, "(in DataMiner.export_file)")

class NullDataMiner(DataMiner):
    '''Returned when a dataminer collection has no dataminer for a data type.'''

    def initialize(self, **kwargs) -> None:
        raise Exceptions.NullDataMinerMethodError(self, self.initialize)

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> NoReturn:
        raise Exceptions.NullDataMinerMethodError(self, self.activate)

    def store(self, environment:DataMinerEnvironment.DataMinerEnvironment, dataminer_collections:list["DataMinerCollection.DataMinerCollection"]) -> NoReturn:
        raise Exceptions.NullDataMinerMethodError(self, self.store)

    def get_accessor(self, file_type:str) -> NoReturn:
        raise Exceptions.NullDataMinerMethodError(self, self.get_accessor)
