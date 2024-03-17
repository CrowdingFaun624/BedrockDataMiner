import json
import traceback
from typing import Any, cast, Literal, TypedDict

import Utilities.Nbt.NbtTypes as NbtTypes
import Utilities.Nbt.NbtReader as NbtReader

NbtTypedDict = TypedDict("NbtTypedDict", {"$special_type": Literal["nbt"], "data": str})

custom_types = NbtTypedDict

def decode_nbt(data:NbtTypedDict) -> NbtTypes.TAG:
    return NbtReader.unpack_snbt(data["data"])


class SpecialEncoder(json.JSONEncoder):
    def default(self, data:Any) -> Any:
        match data:
            case NbtTypes.TAG():
                return {"$special_type": "nbt", "data": str(data)}
            case _:
                raise TypeError("Object of type %s is not JSON serializable" % (data.__class__.__name__))

def decoder_function(data:dict[str,Any]|custom_types) -> Any:
    if "$special_type" not in data:
        return data
    data = cast(custom_types, data)
    match data["$special_type"]:
        case "nbt":
            return decode_nbt(data)

class SpecialDecoder(json.JSONDecoder):
    def __init__(self) -> None:
        super().__init__(object_hook=decoder_function)

encoder = SpecialEncoder
decoder = SpecialDecoder

def test(data:Any, data_correct_encoded:Any) -> None:
    data_encoded = None
    try:
        data_encoded = json.dumps(data, cls=SpecialEncoder)
    except Exception as e:
        traceback.print_exception(e)
    if data_encoded is None:
        raise RuntimeError("Failed to encode data %s!" % (data))
    if data_encoded != json.dumps(data_correct_encoded):
        raise RuntimeError("Encoded data %s does not match %s!" % (data_encoded, data_correct_encoded))

    data_decoded = None
    try:
        data_decoded = json.loads(data_encoded, cls=SpecialDecoder)
    except Exception as e:
        traceback.print_exception(e)
    if data_decoded is None:
        raise RuntimeError("Failed to decode data %s!" % data_encoded)
    if data != data_decoded:
        raise RuntimeError("Decoded data %s is not equal to original %s!" % (data_decoded, data))

def main() -> None:
    test(NbtTypes.TAG_Compound({"wow": NbtTypes.TAG_String("truly incredible")}), {"$special_type": "nbt", "data": "{wow: \"truly incredible\"}"})
