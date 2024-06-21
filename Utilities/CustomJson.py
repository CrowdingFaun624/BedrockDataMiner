import json
import traceback
from typing import Any, Generic, Literal, TypedDict, TypeVar, cast

import Structure.DataPath as DataPath
import Utilities.Exceptions as Exceptions
import Utilities.FileStorageManager as FileStorageManager
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.Nbt.NbtTypes as NbtTypes

DataPathTypedDict = TypedDict("DataPathTypedDict", {"$special_type": Literal["data_path"], "root": str, "path_items":list[Any], "embedded_data": Any|None})
NbtBytesTypedDict = TypedDict("NbtBytesTypedDict", {"$special_type": Literal["nbt_bytes"], "hash": str})
NbtTypedDict = TypedDict("NbtTypedDict", {"$special_type": Literal["nbt"], "data": str})

custom_types = DataPathTypedDict|NbtBytesTypedDict|NbtTypedDict

dict_type_var = TypeVar("dict_type_var")
data_type_var = TypeVar("data_type_var")
class Coder(Generic[dict_type_var, data_type_var]):

    @classmethod
    def decode(cls, data:dict_type_var) -> data_type_var: ...

    @classmethod
    def encode(cls, data:data_type_var) -> dict_type_var: ...

class DataPathCoder(Coder[DataPathTypedDict, DataPath.DataPath]):

    @classmethod
    def decode(cls, data:DataPathTypedDict) -> DataPath.DataPath:
        return DataPath.DataPath(data["path_items"], data["root"], data["embedded_data"])

    @classmethod
    def encode(cls, data:DataPath.DataPath) -> DataPathTypedDict:
        return {"$special_type": "data_path", "path_items": data.path_items, "root": data.root, "embedded_data": data.embedded_data}

class NbtCoder(Coder[NbtTypedDict, NbtTypes.TAG]):

    @classmethod
    def decode(cls, data: NbtTypedDict) -> NbtTypes.TAG:
        return NbtReader.unpack_snbt(data["data"])

    @classmethod
    def encode(cls, data: NbtTypes.TAG) -> NbtTypedDict:
        return {"$special_type": "nbt", "data": str(data)}

class NbtBytesCoder(Coder[NbtBytesTypedDict, NbtReader.NbtBytes]):

    @classmethod
    def decode(cls, data: NbtBytesTypedDict) -> NbtReader.NbtBytes:
        return NbtReader.NbtBytes(data_hash=data["hash"])

    @classmethod
    def encode(cls, data: NbtReader.NbtBytes) -> NbtBytesTypedDict:
        file_hash = FileStorageManager.archive_data(data.read(), ".nbt")
        return {"$special_type": "nbt_bytes", "hash": file_hash}

class SpecialEncoder(json.JSONEncoder):

    def default(self, data:Any) -> custom_types:
        match data:
            case DataPath.DataPath():
                return DataPathCoder.encode(data)
            case NbtReader.NbtBytes(): # stored as raw bytes because data (like endianness) can be lost upon conversion to other format
                return NbtBytesCoder.encode(data)
            case NbtTypes.TAG():
                return NbtCoder.encode(data)
            case _:
                raise Exceptions.CannotEncodeToJsonError(data)

def decoder_function(data:dict[str,Any]|custom_types) -> Any:
    if "$special_type" not in data:
        return data
    data = cast(custom_types, data)
    match data["$special_type"]:
        case "data_path":
            return DataPathCoder.decode(data)
        case "nbt_bytes":
            return NbtBytesCoder.decode(data)
        case "nbt":
            return NbtCoder.decode(data)
        case _:
            raise Exceptions.InvalidSpecialTypeError(data["$special_type"])

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
        raise Exceptions.CustomJsonTestFailError("Failed to encode data %s!" % (data))
    if data_encoded != json.dumps(data_correct_encoded):
        raise Exceptions.CustomJsonTestFailError("Encoded data %s does not match %s!" % (data_encoded, data_correct_encoded))

    data_decoded = None
    try:
        data_decoded = json.loads(data_encoded, cls=SpecialDecoder)
    except Exception as e:
        traceback.print_exception(e)
    if data_decoded is None:
        raise Exceptions.CustomJsonTestFailError("Failed to decode data %s!" % data_encoded)
    if data != data_decoded:
        raise Exceptions.CustomJsonTestFailError("Decoded data %s is not equal to original %s!" % (data_decoded, data))

def main() -> None:
    test(NbtTypes.TAG_Compound({"wow": NbtTypes.TAG_String("truly incredible")}), {"$special_type": "nbt", "data": "{wow: \"truly incredible\"}"})
