import json
from typing import Any, Generic, TypeVar

import Component.Types as Types
import Utilities.Exceptions as Exceptions

dict_type_var = TypeVar("dict_type_var")
data_type_var = TypeVar("data_type_var")

class Coder(Generic[dict_type_var, data_type_var]):

    special_type_name:str

    @classmethod
    def decode(cls, data:dict_type_var) -> data_type_var: ...

    @classmethod
    def encode(cls, data:data_type_var) -> dict_type_var: ...

class SpecialEncoder(json.JSONEncoder):

    def default(self, data:Any) -> Any:
        if (coder := Types.json_encoders.get(type(data))) is not None:
            return coder.encode(data)
        else:
            raise Exceptions.CannotEncodeToJsonError(data)

def decoder_function(data:dict[str,Any]|Any) -> Any:
    if "$special_type" not in data:
        return data
    elif (coder := Types.json_decoders.get(data["$special_type"])) is not None:
        return coder.decode(data)
    else:
        raise Exceptions.InvalidSpecialTypeError(data["$special_type"])

class SpecialDecoder(json.JSONDecoder):

    def __init__(self) -> None:
        super().__init__(object_hook=decoder_function)

encoder = SpecialEncoder
decoder = SpecialDecoder
