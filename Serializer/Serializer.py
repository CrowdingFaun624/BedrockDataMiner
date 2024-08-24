import enum
import json
from typing import Generic, TypeVar

import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

a = TypeVar("a")
'''JSON form of the object.'''
b = TypeVar("b")
'''The object this Serializer deals with.'''

class Mode(enum.Enum):
    binary = "b"
    text = "t"

class Serializer(Generic[a, b]):

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

    mode:Mode
    '''
    Controls if the file is opened in binary or text mode. Must be overridden
    by subclasses of Serializer.
    '''

    def __init__(self, name:str, **kwargs:Any) -> None:
        self.name = name

    def __repr__(self) -> str:
        return "<%s %s>" % (self.__class__.__name__, self.name)

    def serialize_json(self, data:a) -> b:
        '''
        Converts an object into JSON. Will be called when storing data in a
        version's data file, or when `serialize` is not overridden.
        '''
        raise Exceptions.SerializerMethodNonexistentError(self, self.serialize_json)

    def serialize(self, data:a) -> str|bytes:
        '''
        Converts an object into a file. Will be called when storing the file in
        file storage. By default, calls `serialize_json` and converts it to a
        string.
        '''
        return json.dumps(self.serialize_json(data))

    def deserialize_json(self, data:b) -> a:
        '''
        Converts JSON into an object. Will be called when retrieving data from
        a version's data file, or when `deserialize` is not overridden.
        '''
        raise Exceptions.SerializerMethodNonexistentError(self, self.deserialize_json)

    def deserialize(self, data:str|bytes) -> a:
        '''
        Converts a file into an object. Will be called when retrieving the file
        from file storage. By default, attempts to read the data as JSON, and
        call `deserialize_json` on that.
        '''
        if isinstance(data, str):
            return self.deserialize_json(json.loads(data))
        else:
            raise Exceptions.SerializerMethodNonexistentError(self, self.deserialize)
