from typing import Any, ClassVar, Mapping

import Domain.Domain as Domain
from Component.ComponentObject import ComponentObject
from Utilities.Exceptions import SerializerMethodNonexistentError
from Utilities.TypeVerifier import TypedDictTypeVerifier


class SerializerCreator(ComponentObject):

    __slots__ = (
        "arguments",
        "created_serializer",
        "serializer",
        "serializer_class",
    )

    def link_serializer_creator(self, arguments:Mapping[Any, Any], serializer_class:type["Serializer"]) -> None:
        self.arguments = arguments
        self.serializer_class = serializer_class
        self.created_serializer = False

    def finalize_serializer_creator(self) -> None:
        if self.created_serializer: return
        self.created_serializer = True
        self.serializer = self.serializer_class(self.name, self.full_name, self.domain, self.arguments)
        self.serializer.finalize()

class Serializer[a]():

    __slots__ = (
        "domain",
        "full_name",
        "memory_constrained",
        "name",
    )

    type_verifier:ClassVar[TypedDictTypeVerifier] = TypedDictTypeVerifier()
    '''
    TypeVerifier for verifying the arguments of this Serializer
    '''

    empty_okay:bool = False
    '''
    If False, an EmptyFileError will be raised if attempting to create a File
    object with this Serializer with an empty bytes object.
    '''

    can_contain_subfiles:bool = False
    '''
    If True, will call get_referenced_files during garbage collection.
    '''

    def __init__(self, name:str, full_name:str, domain:"Domain.Domain", kwargs:Mapping[str,Any]) -> None:
        self.name = name
        self.full_name = full_name
        self.domain = domain
        self.memory_constrained:bool = False
        self.initialize(**kwargs)

    def initialize(self, **kwargs:Any) -> None:
        pass

    def finalize(self) -> None:
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"

    def memory_constrain(self) -> None:
        '''
        Called when memory is too high.
        '''
        self.memory_constrained = True

    def deserialize(self, data:bytes) -> a:
        '''
        Converts a file into an object. Will be called when retrieving the file
        from file storage.
        '''
        raise SerializerMethodNonexistentError(self, self.deserialize)
