from typing import Any, NoReturn

import Dataminer.DataminerEnvironment as DataminerEnvironment
import Dataminer.DataminerSettings as DataminerSettings
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.TypeVerifier as TypeVerifier
import Version.Version as Version


class Dataminer():

    parameters:TypeVerifier.TypeVerifier|None = TypeVerifier.TypedDictTypeVerifier()
    '''TypeVerifier for verifying the json arguments of this Dataminer'''

    def __init__(self, version:Version.Version, settings:DataminerSettings.DataminerSettings) -> None:
        self.version = version
        self.settings = settings
        self.domain = self.settings.domain
        self.file_name = self.settings.file_name
        self.name = self.settings.name
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
            options:list[str] = [version_file_type.name for version_file_type in self.files if self.version.get_accessor(version_file_type.name, accessor_type) is not None]
            raise Exceptions.DataminerFileTypePermissionError(self, file_type, options)
        if len(self.files_str) == 0:
            raise Exceptions.DataminerNoFileTypeError(self)
        elif len(self.files_str) > 1:
            raise Exceptions.DataminerCannotKnowFileTypeError(self, len(self.files_str))
        elif file_type is None:
            file_type = next(iter(self.files_str))
        accessor = self.version.get_accessor(file_type, accessor_type)
        if accessor is None:
            options:list[str] = [version_file_type.name for version_file_type in self.files if self.version.get_accessor(version_file_type.name, accessor_type) is not None]
            raise Exceptions.DataminerAccessorWrongTypeError(self, file_type, accessor_type, options)
        return accessor

    def export_file(self, file_bytes:bytes, file_name:str) -> File.File:
        return File.new_file(file_bytes, file_name)

class NullDataminer(Dataminer):
    '''Returned when a dataminer collection has no dataminer for a data type.'''

    def initialize(self, **kwargs) -> None:
        raise Exceptions.NullDataminerMethodError(self, self.initialize)

    def activate(self, environment:DataminerEnvironment.DataminerEnvironment) -> NoReturn:
        raise Exceptions.NullDataminerMethodError(self, self.activate)

    def get_accessor(self, file_type:str) -> NoReturn:
        raise Exceptions.NullDataminerMethodError(self, self.get_accessor)
