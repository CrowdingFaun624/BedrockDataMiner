from typing import TYPE_CHECKING, Any

import Domain.Domain as Domain
import Utilities.TypeVerifier as TypeVerifier

if TYPE_CHECKING:
    import Version.Version as Version

class Accessor():

    linked_accessors:dict[str, type["Accessor"]] = {}
    instance_parameters:TypeVerifier.TypedDictTypeVerifier = TypeVerifier.TypedDictTypeVerifier()
    propagated_parameters:TypeVerifier.TypedDictTypeVerifier = TypeVerifier.TypedDictTypeVerifier()
    class_parameters:TypeVerifier.TypeVerifier = TypeVerifier.TypedDictTypeVerifier()

    __slots__ = (
        "accessor_type_name",
        "domain",
        "version",
    )

    def __init__(self, name:str, version:"Version.Version", domain:"Domain.Domain", instance_arguments:dict[str,Any], class_arguments:dict[str,Any], propagated_arguments:dict[str,Any], linked_accessors:dict[str,"Accessor"]) -> None:
        '''
        :version: Version object this accessor is based on.
        :location: File location to the directory containing extracted files.
        '''
        self.accessor_type_name = name
        self.version = version
        self.domain = domain
        self.prepare_for_install(instance_arguments, class_arguments, propagated_arguments, linked_accessors)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.accessor_type_name} for {self.version.name}>"

    def prepare_for_install(self, instance_arguments:dict[str,Any], class_arguments:dict[str,Any], propagated_arguments:dict[str,Any], linked_accessors:dict[str,"Accessor"]) -> None:
        '''Any actions that can take place before grabbing files can happen.'''
        ...

    def all_done(self) -> None:
        '''Removes all files that were created as part of the installation of this version.'''
        ...

    def get_referenced_files(self, get_referenced_files:set[int]) -> None:
        ...
