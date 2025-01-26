from typing import Any

import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier


class Serializer[a, b]():

    type_verifier:TypeVerifier.TypeVerifier = TypeVerifier.TypedDictTypeVerifier()
    '''
    TypeVerifier for verifying the arguments of this Serializer
    '''

    store_as_file_default = True
    '''
    If True, the file will be stored in file storage and deserialized on
    demand. If False, the deserialized data will be stored in the data files
    for each version.
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

    linked_serializers:dict[str,type["Serializer"]] = {}

    def __init__(self, name:str, domain:"Domain.Domain", **kwargs:Any) -> None:
        self.name = name
        self.domain = domain

    def link_finals(self, linked_serializers:dict[str,"Serializer"]) -> None:
        self.get_linked_serializers(linked_serializers)

    def get_linked_serializers(self, linked_serializers:dict[str,"Serializer"]) -> None:
        # Serializers override this to let themselves reference other Serializers.
        ...

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

    def get_referenced_files(self, data:bytes, referenced_files:set[int]) -> None:
        '''
        If this Serializer returns a File object, this function should return
        the hashes of those files within the given file.
        '''
        ...
