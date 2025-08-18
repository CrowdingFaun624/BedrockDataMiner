from typing import TYPE_CHECKING, Any, Mapping

import Domain.Domain as Domain
from Utilities.TypeVerifier import TypedDictTypeVerifier, TypeVerifier

if TYPE_CHECKING:
    from Version.Version import Version

class Accessor():

    linked_accessor_types:dict[str, type["Accessor"]] = {}
    instance_parameters:TypedDictTypeVerifier = TypedDictTypeVerifier()
    class_parameters:TypeVerifier = TypedDictTypeVerifier()

    __slots__ = (
        "constrained_memory",
        "domain",
        "full_name",
        "linked_accessors",
        "version",
    )

    def __init__(
            self,
            full_name:str,
            version:"Version",
            domain:"Domain.Domain",
            instance_arguments:Any,
            class_arguments:Any,
            linked_accessors:dict[str,"Accessor"],
        ) -> None:
        self.full_name = full_name
        self.version = version
        self.domain = domain
        self.linked_accessors = linked_accessors
        self.constrained_memory:bool = False
        self.prepare_for_install(instance_arguments, class_arguments, linked_accessors)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_name}>"

    def prepare_for_install(self, instance_arguments:Mapping[Any,Any], class_arguments:Mapping[Any,Any], linked_accessors:dict[str,"Accessor"]) -> None:
        """
        Any actions that can take place before grabbing files can happen.
        """
        ...

    def close(self) -> None:
        """
        Always called by the system before deleting this Accessor.
        """
        for linked_accessor in self.linked_accessors.values():
            linked_accessor.close()

    def all_done(self) -> None:
        """
        Removes all files that were created as part of the installation of this version.
        Should only be called on the parent Accessor.
        """
        for linked_accessor in self.linked_accessors.values():
            linked_accessor.all_done()

    def constrain_memory(self) -> None:
        """
        Called when memory is too high.
        """
        self.constrained_memory = True
        for linked_accessor in self.linked_accessors.values():
            linked_accessor.constrain_memory()

    def get_referenced_files(self, referenced_files:set[int]) -> None:
        for linked_accessor in self.linked_accessors.values():
            linked_accessor.get_referenced_files(referenced_files)
