import json
from typing import Any, Iterator

import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


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

    def __init__(self, name:str, domain:"Domain.Domain", **kwargs:Any) -> None:
        self.name = name
        self.domain = domain

    def finalize(self) -> None:
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"

    def serialize_json(self, data:a) -> b:
        '''
        Converts an object into JSON. Will be called when storing data in a
        version's data file, or when `serialize` is not overridden.
        '''
        raise Exceptions.SerializerMethodNonexistentError(self, self.serialize_json)

    def serialize(self, data:a) -> bytes:
        '''
        Converts an object into a file. Will be called when storing the file in
        file storage. By default, calls `serialize_json` and converts it to a
        string.
        '''
        return json.dumps(self.serialize_json(data)).encode()

    def deserialize_json(self, data:b) -> a:
        '''
        Converts JSON into an object. Will be called when retrieving data from
        a version's data file, or when `deserialize` is not overridden.
        '''
        raise Exceptions.SerializerMethodNonexistentError(self, self.deserialize_json)

    def deserialize(self, data:bytes) -> a:
        '''
        Converts a file into an object. Will be called when retrieving the file
        from file storage. By default, attempts to read the data as JSON, and
        call `deserialize_json` on that.
        '''
        raise Exceptions.SerializerMethodNonexistentError(self, self.deserialize)

    def get_referenced_files(self, data:bytes) -> Iterator[int]:
        '''
        If this Serializer returns a File object, this function should return
        the hashes of those files within the given file.
        '''
        return; yield
