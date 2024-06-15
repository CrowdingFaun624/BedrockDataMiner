from typing import TYPE_CHECKING, Any

import Downloader.Accessor as Accessor
import Downloader.Manager as Manager
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Version.VersionFileType as VersionFileType

if TYPE_CHECKING:
    import Version.Version as Version

class AccessorType():

    def __init__(self, name:str) -> None:
        self.name = name
        self.manager_class:type[Manager.Manager]|None = None
        self.accessor_class:type[Accessor.Accessor]|None = None
        self.parameters:TypeVerifier.TypeVerifier|None = None

    def link_finals(
        self,
        manager_class:type[Manager.Manager],
        accessor_class:type[Accessor.Accessor],
        parameters:TypeVerifier.TypeVerifier,
    ) -> None:
        self.manager_class = manager_class
        self.accessor_class = accessor_class
        self.parameters = parameters

    def get_manager_class(self) -> type[Manager.Manager]:
        if self.manager_class is None:
            raise Exceptions.AttributeNoneError("manager_class", self)
        return self.manager_class

    def get_accessor_class(self) -> type[Accessor.Accessor]:
        if self.accessor_class is None:
            raise Exceptions.AttributeNoneError("accessor_class", self)
        return self.accessor_class

    def get_parameters(self) -> TypeVerifier.TypeVerifier:
        if self.parameters is None:
            raise Exceptions.AttributeNoneError("parameters", self)
        return self.parameters

    def create_accessor(self, version:"Version.Version", file_type:VersionFileType.VersionFileType, accessor_arguments:Any) -> Accessor.Accessor:
        manager = self.get_manager_class()(version, accessor_arguments, version.get_version_directory().joinpath(file_type.install_location))
        return self.get_accessor_class()(self.name, manager, version, accessor_arguments)
