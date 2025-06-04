from typing import (
    Any,
    Literal,
    MutableMapping,
    MutableSequence,
    Optional,
    TypedDict,
    cast,
)

from Utilities.Exceptions import StructureException, message

__all__ = ("volume_normalize_nbt",)

LAYER_CHARACTERS_DEFAULT_MAX = len("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_-+={[}];:'<,>./?αβγδεζηθικλμνξπρσςτυφχψωΓΔΘΛΞΠΣΦΨΩБбгДдËëЖжЗзИиЙйЛлФфЦцЧчШшЩщЪъЫыЬьЭэЮюЯя")


class VolumeStructureMissingKeyError(StructureException):
    "The VolumeStructure is missing its position or state key."

    def __init__(self, key_type:Literal["Position", "State"], key:str, block:int, message:Optional[str]=None) -> None:
        '''
        :key_type: If the key is a position key or a state key.
        :key: The key that is missing.
        :block: The index of the block with the missing key.
        :message: Additional text to place after the main message.
        '''
        super().__init__(key_type, key, block, message)
        self.key_type = key_type
        self.key = key
        self.block = block
        self.message = message

    def __str__(self) -> str:
        return f"{self.key_type} key \"{self.key}\" is missing in block {self.block}{message(self.message)}"

class VolumeStructureInvalidKeyError(StructureException):
    "The position or state of a VolumeStructure is invalid."

    def __init__(self, key_type:Literal["Position", "State"], value:Any, block:int, message:str="is invalid") -> None:
        '''
        :key_type: If the key is a position key or a state key.
        :value: The value of the key for this block.
        :block: The index of the block.
        :message: Additional text to place after the main message.
        '''
        super().__init__(key_type, value, block, message)
        self.key_type = key_type
        self.value = value
        self.block = block
        self.message = message

    def __str__(self) -> str:
        return f"{self.key_type} \"{self.value}\" in block {self.block} {self.message}!"

class OutputTypedDict(TypedDict):
    states: dict[tuple[int,int,int],int]
    data: dict[tuple[int,int,int],MutableMapping[str,Any]]
    size: tuple[int,int,int]

def volume_normalize_nbt(data:MutableSequence[MutableMapping[str,Any]], position_key:str, state_key:str, layer_characters_len:int=LAYER_CHARACTERS_DEFAULT_MAX) -> OutputTypedDict:
    max_x, max_y, max_z = 0, 0, 0
    states:dict[tuple[int,int,int],int] = {}
    additional_data:dict[tuple[int,int,int],MutableMapping[str,Any]] = {}
    for index, block in enumerate(data):
        position_list = block.get(position_key, None)
        state = block.get(state_key, None)

        if position_list is None:
            raise VolumeStructureMissingKeyError("Position", position_key, index)
        if state is None:
            raise VolumeStructureMissingKeyError("State", state_key, index)
        try: # try except because it could be a not-list, which would raise an exception on the tuple() call.
            if len(position_list) != 3:
                raise VolumeStructureInvalidKeyError("Position", position_list, index, "is not length 3")
            position:tuple[int,int,int] = cast(tuple[int,int,int], tuple(position_list))
        except Exception:
            raise VolumeStructureInvalidKeyError("Position", position_list, index)
        if not all(isinstance(axis, int) for axis in position):
            raise VolumeStructureInvalidKeyError("Position", position, index, "has an axis that is not an int")
        if not isinstance(state, int):
            raise VolumeStructureInvalidKeyError("State", state, index, "is not an int")
        weird_axes = [(axis, label) for axis, label in zip(position, "xyz") if axis < 0]
        if len(weird_axes) > 0:
            raise VolumeStructureInvalidKeyError("Position", position, index, "has an axis that is less than 0")
        if state >= layer_characters_len:
            raise VolumeStructureInvalidKeyError("State", state, index, f"is at least {layer_characters_len}, the maximum for this VolumeStructure")

        max_x, max_y, max_z = max(max_x, position[0]), max(max_y, position[1]), max(max_z, position[2])
        states[position] = int(state)
        if len(block) > 2:
            additional_data[position] = type(block)()
            additional_data[position].update((key, value) for key, value in block.items() if key != position_key and key != state_key)
    return {
        "states": states,
        "data": additional_data,
        "size": (max_x + 1, max_y + 1, max_z + 1)
    }
