from typing import Any

import Domain.Domain as Domain
from Utilities.Exceptions import SerializerMethodNonexistentError
from Utilities.TypeVerifier import TypeVerifier


class Serializer[a]():

    __slots__ = (
        "domain",
        "full_name",
        "memory_constrained",
        "name",
    )

    type_verifier:TypeVerifier = TypeVerifier()
    '''
    TypeVerifier for verifying the arguments of this Serializer
    '''

    empty_okay = False
    '''
    If False, an EmptyFileError will be raised if attempting to create a File
    object with this Serializer with an empty bytes object.
    '''

    can_contain_subfiles = False
    '''
    If True, will call get_referenced_files during garbage collection.
    '''

    def __init__(self, name:str, full_name:str, domain:"Domain.Domain", kwargs:dict[str,Any]) -> None:
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
