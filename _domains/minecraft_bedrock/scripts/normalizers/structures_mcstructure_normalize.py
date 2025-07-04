from itertools import count, product
from typing import Any, NotRequired, TypedDict, cast

from Component.ComponentFunctions import component_function


class BlockPaletteItemTypedDict(TypedDict):
    name: str
    states: dict[str,Any]
    version: int

class BlockPositionDataTypedDict(TypedDict):
    block_entity_data: dict[str,Any]
    tick_delay: list[Any]
    tick_queue_data: list[Any]

class DefaultPaletteTypedDict(TypedDict):
    block_palette: list[BlockPaletteItemTypedDict]
    block_position_data: NotRequired[dict[str,BlockPositionDataTypedDict]]

class PaletteTypedDict(TypedDict):
    default: DefaultPaletteTypedDict

class LayerTypedDict(TypedDict):
    states: dict[tuple[int,int,int],int]
    additional_data: dict[tuple[int,int,int],BlockPositionDataTypedDict]
    size: tuple[int,int,int]

class StructureTypedDict(TypedDict):
    entities: list[Any]
    palette: PaletteTypedDict
    block_indices: NotRequired[list[list[int]]]
    layers: list[LayerTypedDict] # placed here by me.

class FileTypedDict(TypedDict):
    format_version: int
    size: list[int]
    structure_world_origin: list[int]
    structure: StructureTypedDict

def get_layer_states(
    layer:list[int],
    size:tuple[int,int,int],
    palette:list[BlockPaletteItemTypedDict],
    blocks_position_data:dict[int,BlockPositionDataTypedDict],
    is_last_layer:bool,
) -> tuple[dict[tuple[int,int,int],int],dict[tuple[int,int,int],BlockPositionDataTypedDict]]:
    states:dict[tuple[int,int,int],int] = {}
    additional_data:dict[tuple[int,int,int],BlockPositionDataTypedDict] = {}
    for index, (x, y, z), state in zip(count(), product(range(size[0]), range(size[1]), range(size[2])), layer):
        state_name = palette[state]["name"] if state >= 0 and state < len(palette) else None
        if (position_data := blocks_position_data.get(index)) is not None:
            if is_last_layer or (
                (block_entity_data := position_data.get("block_entity_data")) is not None
                and state_name is not None
                and (entity_data_id := cast(str|None, block_entity_data.get("id"))) is not None
                and entity_data_id.lower() == state_name.split(":", maxsplit=1)[1]
            ):
                # remove it so other layers don't look at it again.
                blocks_position_data.pop(index)
                additional_data[x, y, z] = position_data
        if state != -1:
            states[x, y, z] = state
    return states, additional_data

@component_function(no_arguments=True)
def structures_mcstructure_normalize(data:FileTypedDict) -> None:
    size_x, size_y, size_z = data["size"]
    palette = data["structure"]["palette"]["default"]
    block_palette = palette["block_palette"]
    position_data = {int(key): value for key, value in palette.pop("block_position_data").items()}
    # the block indices are reversed because we want the last one to be
    # processed first. Both layers share the same palette, but the second layer
    # contains few blocks, so it is unlikely for any block entities to be
    # assigned to them. If the first layer is processed last, it will know that
    # it must assign the block entities now, lest they never be assigned.
    block_indices = data["structure"].pop("block_indices")
    data["structure"]["layers"] = layers = []
    for layer_index, layer in enumerate(reversed(block_indices)):
        is_last_layer = layer_index == len(block_indices) - 1
        states, additional_data = get_layer_states(layer, (size_x, size_y, size_z), block_palette, position_data, is_last_layer)
        layers.append({"states": states, "data": additional_data, "size": (size_x, size_y, size_z)})
    layers.reverse() # re-reverse (or "verse" as they call it.)
