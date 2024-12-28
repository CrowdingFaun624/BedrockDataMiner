import json
from typing import Any

import Component.Types as Types
import Utilities.Exceptions as Exceptions


class Coder[A, B]():

    special_type_name:str

    @classmethod
    def decode(cls, data:A) -> B: ...

    @classmethod
    def encode(cls, data:B) -> A: ...

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
