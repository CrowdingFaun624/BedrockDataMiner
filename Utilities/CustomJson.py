import json
from typing import Any

import Component.Types as Types
import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions


class Coder[A, B]():

    special_type_name:str

    @classmethod
    def decode(cls, data:A, domain:"Domain.Domain") -> B: ...

    @classmethod
    def encode(cls, data:B, domain:"Domain.Domain") -> A: ...

def get_special_encoder(domain:"Domain.Domain") -> type[json.JSONEncoder]:

    class SpecialEncoder(json.JSONEncoder):

        def default(self, data:Any) -> Any:
            if (coder := Types.json_encoders.get(type(data))) is not None:
                return coder.encode(data, domain)
            else:
                raise Exceptions.CannotEncodeToJsonError(data)

    return SpecialEncoder

def get_special_decoder(domain:"Domain.Domain") -> type[json.JSONDecoder]:

    def decoder_function(data:dict[str,Any]|Any) -> Any:
        if "$special_type" not in data:
            return data
        elif (coder := Types.json_decoders.get(data["$special_type"])) is not None:
            return coder.decode(data, domain)
        else:
            raise Exceptions.InvalidSpecialTypeError(data["$special_type"])

    class SpecialDecoder(json.JSONDecoder):

        def __init__(self) -> None:
            super().__init__(object_hook=decoder_function)

    return SpecialDecoder
