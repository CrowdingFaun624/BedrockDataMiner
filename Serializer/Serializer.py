from typing import Any

import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier


class Serializer[a]():

    type_verifier:TypeVerifier.TypeVerifier = TypeVerifier.TypedDictTypeVerifier()
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

    def __init__(self, name:str, domain:"Domain.Domain", **kwargs:Any) -> None:
        self.name = name
        self.domain = domain

    def finalize(self) -> None:
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"

    def deserialize(self, data:bytes) -> a:
        '''
        Converts a file into an object. Will be called when retrieving the file
        from file storage.
        '''
        raise Exceptions.SerializerMethodNonexistentError(self, self.deserialize)
