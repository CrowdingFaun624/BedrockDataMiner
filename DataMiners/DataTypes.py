import enum
import pyjson5
from typing import Any, Callable, cast, IO, Iterable, Literal, Sequence

import DataMiners.DataMiner as DataMiner
import Utilities.Nbt.NbtReader as NbtReader

class DataTypes(enum.Enum):
    json = "json"
    nbt = "nbt"

    @classmethod
    def data_types(cls) -> list[str]:
        return [item.value for item in cls]
    def get_data_format(self):
        types_dict:dict[DataTypes,Literal["b","t"]] = {DataTypes.json: "t", DataTypes.nbt: "b"}
        return types_dict[self]

def get_data(dataminer:DataMiner.DataMiner, path:str, data_type:DataTypes) -> Any:
    data_format = data_type.get_data_format()
    file_data = dataminer.read_file(path, data_format)
    return get_data_from_content(file_data, data_type)

def get_data_from_content(content:str|bytes|IO, data_type:DataTypes) -> Any:
    if not isinstance(content, str|bytes):
        content = cast(IO, content).read()
    match data_type:
        case DataTypes.json:
            return pyjson5.loads(cast(str, content))
        case DataTypes.nbt:
            return NbtReader.get_nbt_bytes(cast(bytes, content))
        case _:
            raise ValueError()

def get_file_request(files:Iterable[str], data_type:DataTypes) -> Sequence[str|tuple[str,Literal["b", "t"],None|Callable[[IO],Any]]]:
    data_format = data_type.get_data_format()
    data_function:Callable[[IO],Any] = lambda data: get_data_from_content(data, data_type)
    return [(file, data_format, data_function) for file in files]
