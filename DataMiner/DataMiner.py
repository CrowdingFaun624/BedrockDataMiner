import json
from pathlib import Path
from typing import Any, NoReturn

import Dataminer.DataminerEnvironment as DataminerEnvironment
import Dataminer.DataminerSettings as DataminerSettings
import Downloader.Accessor as Accessor
import Serializer.Serializer as Serializer
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Version.Version as Version


class Dataminer():

    parameters:TypeVerifier.TypeVerifier|None = TypeVerifier.TypedDictTypeVerifier()
    '''TypeVerifier for verifying the json arguments of this Dataminer'''
    serializer_names:set[str] = set()
    '''The keys of Serializers given to this Dataminer's settings must match `serializer_names`.'''

    def __init__(self, version:Version.Version, settings:DataminerSettings.DataminerSettings) -> None:
        self.version = version
        self.settings = settings
        self.domain = self.settings.domain
        self.file_name = self.settings.get_file_name()
        self.name = self.settings.get_name()
        self.serializers = self.settings.serializers
        self.files = set(self.settings.get_version_file_types())
        self.files_str = {version_file_type.name for version_file_type in self.files}
        self.dependencies = self.settings.get_dependencies()
        self.dependencies_str = [dependency.name for dependency in self.dependencies]
        if not isinstance(self, NullDataminer) and self.version not in self.settings.get_version_range():
            raise Exceptions.VersionOutOfRangeError(self.version, self.settings.version_range, f"in Dataminer {self}")

        self.initialize(**settings.arguments)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name} on {self.version.name}>"

    @classmethod
    def manipulate_arguments(cls, arguments:dict[str,Any]) -> None:
        '''Manipulates the arguments of this Dataminer before they are passed into `initialize`.'''
        return None

    def initialize(self, **kwargs) -> None:
        '''`DataminerSettings.__init__(**kwargs)` -> `Dataminer.initialize(**kwargs)`.'''
        pass

    def activate(self, environment:DataminerEnvironment.DataminerEnvironment) -> Any:
        '''Makes the dataminer get the file. Returns the output.'''
        raise Exceptions.DataminerLacksActivateError(self)

    def get_data_file_path(self) -> Path:
        return self.version.get_data_directory().joinpath(self.file_name)

    def get_data_file(self) -> Any:
        with open(self.get_data_file_path(), "rt") as f:
            return json.load(f, cls=self.domain.json_decoder)

    def get_accessor[a: Accessor.Accessor](self, file_type:str, accessor_type:type[a]=Accessor.Accessor) -> a:
        if file_type not in self.files_str:
            raise Exceptions.DataminerFileTypePermissionError(self, file_type, sorted(self.files_str))
        accessor = self.version.get_accessor(file_type, accessor_type)
        if accessor is None:
            raise Exceptions.DataminerAccessorWrongTypeError(self, file_type, accessor_type)
        return accessor

    def get_serializer(self, serializer_key:str) -> Serializer.Serializer:
        if self.serializers is None:
            raise Exceptions.AttributeNoneError("serializers", self)
        serializer = self.serializers.get(serializer_key)
        if serializer is None:
            raise Exceptions.DataminerUnrecognizedSerializerError(self, serializer_key)
        return serializer

    def export_file(self, file_bytes:bytes, file_name:str, serializer_key:str="main") -> File.File|Any:
        serializer = self.get_serializer(serializer_key)
        if serializer.store_as_file_default:
            return File.new_file(file_bytes, file_name, serializer)
        else:
            try:
                return serializer.deserialize(file_bytes)
            except Exception:
                raise Exceptions.SerializationFailureError(serializer, file_name, "(in Dataminer.export_file)")

class NullDataminer(Dataminer):
    '''Returned when a dataminer collection has no dataminer for a data type.'''

    def initialize(self, **kwargs) -> None:
        raise Exceptions.NullDataminerMethodError(self, self.initialize)

    def activate(self, environment:DataminerEnvironment.DataminerEnvironment) -> NoReturn:
        raise Exceptions.NullDataminerMethodError(self, self.activate)

    def get_accessor(self, file_type:str) -> NoReturn:
        raise Exceptions.NullDataminerMethodError(self, self.get_accessor)
