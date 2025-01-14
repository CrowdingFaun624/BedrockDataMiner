import json
from pathlib import Path
from typing import Any, NoReturn

import Dataminer.DataminerEnvironment as DataminerEnvironment
import Dataminer.DataminerSettings as DataminerSettings
import Downloader.Accessor as Accessor
import Serializer.Serializer as Serializer
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.TypeVerifier as TypeVerifier
import Version.Version as Version


class Dataminer():

    parameters:TypeVerifier.TypeVerifier|None = TypeVerifier.TypedDictTypeVerifier()
    '''TypeVerifier for verifying the json arguments of this Dataminer'''
    serializer_types:dict[str,type[Serializer.Serializer]] = {}
    '''The keys of Serializers given to this Dataminer's settings must match `serializer_types`.'''

    def __init__(self, version:Version.Version, settings:DataminerSettings.DataminerSettings) -> None:
        self.version = version
        self.settings = settings
        self.domain = self.settings.domain
        self.file_name = self.settings.file_name
        self.name = self.settings.name
        self.serializers = self.settings.serializers
        self.files = set(self.settings.version_file_types)
        self.files_str = {version_file_type.name for version_file_type in self.files}
        self.dependencies = self.settings.dependencies
        self.dependencies_str = [dependency.name for dependency in self.dependencies]
        if not isinstance(self, NullDataminer) and self.version not in self.settings.version_range:
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

    def get_accessor[a: Accessor.Accessor](self, accessor_type:type[a]=Accessor.Accessor, file_type:str|None=None) -> a:
        if file_type is not None and file_type not in self.files_str:
            raise Exceptions.DataminerFileTypePermissionError(self, file_type, sorted(self.files_str))
        if len(self.files_str) == 0:
            raise Exceptions.DataminerNoFileTypeError(self)
        elif len(self.files_str) > 1:
            raise Exceptions.DataminerCannotKnowFileTypeError(self, len(self.files_str))
        elif file_type is None:
            file_type = next(iter(self.files_str))
        accessor = self.version.get_accessor(file_type, accessor_type)
        if accessor is None:
            raise Exceptions.DataminerAccessorWrongTypeError(self, file_type, accessor_type)
        return accessor

    def get_serializer(self, serializer_key:str) -> Serializer.Serializer:
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
