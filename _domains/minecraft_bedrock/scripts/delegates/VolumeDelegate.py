import math
from itertools import product
from types import EllipsisType
from typing import Any, MutableMapping, TypedDict, cast

import Domain.Domain as Domain
import Structure.Container as Con
import Structure.Delegate.LineDelegate as LineDelegate
import Structure.Difference as Diff
import Structure.IterableContainer as ICon
import Structure.SimpleContainer as SCon
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureTypes.DictStructure as DictStructure
import Structure.StructureTypes.KeymapStructure as KeymapStructure
import Structure.StructureTypes.MappingStructure as MappingStructure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

LAYER_CHARACTERS_DEFAULT = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_-+={[}];:'<,>./?αβγδεζηθικλμνξπρσςτυφχψωΓΔΘΛΞΠΣΦΨΩБбгДдËëЖжЗзИиЙйЛлФфЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"

__all__ = ("VolumeDelegate",)

# class ContainerTypedDict(TypedDict):
#     states: ICon.ICon[SCon.SCon[tuple[int,int,int]], SCon.SCon[int], dict[tuple[int,int,int],int]]
#     data: ICon.ICon[SCon.SCon[tuple[int,int,int]], ICon.ICon[Any, Any, MutableMapping[Any, Any]], dict[tuple[int,int,int],MutableMapping[Any, Any]]]
#     size: ICon.ICon[SCon.SCon[int], SCon.SCon[int], tuple[int,int,int]]

class DataTypedDict(TypedDict):
    states: dict[tuple[int,int,int],int]
    data: dict[tuple[int,int,int],MutableMapping[Any,Any]]
    size: tuple[int,int,int]

class VolumeDelegate(LineDelegate.LineDelegate[
    ICon.ICon[Any, Any, DataTypedDict],
    ICon.IDon[Diff.Diff[Any], Diff.Diff[Any], DataTypedDict, Any, Any],
    KeymapStructure.KeymapStructure[Any, Any, DataTypedDict, Any, Any, Any, Any, list[LineDelegate.LineType], list[LineDelegate.LineType]],
]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("field", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("layer_characters", False, str, lambda key, value: (len(value) == len(set(value)), "all characters must be unique")),
        TypeVerifier.TypedDictKeyTypeVerifier("print_additional_data", False, bool),
    )

    applies_to = (KeymapStructure.KeymapStructure,)

    def __init__(
        self,
        structure:KeymapStructure.KeymapStructure,
        keys:dict[str,Any],
        field:str="block",
        layer_characters:str=LAYER_CHARACTERS_DEFAULT,
        print_additional_data:bool=True,
    ) -> None:
        super().__init__(structure, keys, field, passthrough=False)
        self.layer_characters = layer_characters
        self.print_additional_data = print_additional_data

    def finalize(self, domain:"Domain.Domain", trace:Trace.Trace) -> None:
        super().finalize(domain, trace)
        structure = cast(DictStructure.DictStructure[Any, Any, Any, Any, Any, Any, Any, list[LineDelegate.LineType], list[LineDelegate.LineType]], self.structure.value_structures["data"])
        substructure = structure.value_structure
        if substructure is None or not isinstance(substructure, MappingStructure.MappingStructure):
            raise TypeError(f"Substructure of {self} is not an AbstractMappingStructure, but instead {substructure}!")
        self.substructure = substructure

    def print_layer(
        self,
        states:dict[tuple[int,int,int], int],
        additional_data:ICon.ICon[SCon.SCon[tuple[int,int,int]], ICon.ICon[Any, Any, MutableMapping[Any, Any]], dict[tuple[int,int,int],MutableMapping[Any, Any]]]|None,
        layer:int,
        size:tuple[int,...],
        trace:Trace.Trace,
        environment:StructureEnvironment.PrinterEnvironment,
    ) -> list[LineDelegate.LineType]:
        layer_2d = [[" "] * size[0] for z in range(size[2])] # create empty horizontal slice.
        for x, z in product(range(size[0]), range(size[2])):
            if (state := states.get((x, layer, z))) is not None:
                layer_2d[z][x] = self.layer_characters[state] # replace each item in horizontal slice with corresponding character.
        x_axis_size = math.ceil(math.log10(size[0] + 1)) # how tall the horizontal axis is
        z_axis_size = math.ceil(math.log10(size[2] + 1)) # how wide the vertical axis is
        x_labels = [str(i) for i in range(size[0])]
        z_labels = [str(i) for i in range(size[2])]
        for i in range(size[0]): # pad all labels with appropriate amount of spaces.
            x_labels[i] = " " * (x_axis_size - len(x_labels[i])) + x_labels[i]
        for i in range(size[2]):
            z_labels[i] = " " * (z_axis_size - len(z_labels[i])) + z_labels[i]
        output_grid:list[list[str]] = []
        for i in range(x_axis_size):
            output_grid.append(([" "] * (z_axis_size + 1)) + [x_labels[j][i] for j in range(size[0])])
        output_grid.append([])
        for i in range(size[2]):
            output_grid.append(list(z_labels[i] + " ") + layer_2d[i])
        output:list[LineDelegate.LineType] = [(0, "".join(line)) for line in output_grid]
        if self.print_additional_data and additional_data is not None:
            for position, block_data in additional_data.items():
                if position.data[1] != layer: continue
                substructure_output:list[LineDelegate.LineType]|EllipsisType = self.substructure.print_branch(block_data, trace, environment)
                if substructure_output is ...:
                    continue
                output.append((0, f"{self.field} at {position.data}"))
                output.extend((indentation + 1, line) for indentation, line in substructure_output)
        return output

    def print_branch(self, data: ICon.ICon[Con.Con, Any, DataTypedDict], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> list[tuple[int, str]] | EllipsisType:
        data_dict = data.data
        output:list[LineDelegate.LineType] = []
        size_tuple = data_dict["size"]
        states = data_dict["states"]
        additional_data:ICon.ICon[SCon.SCon[tuple[int,int,int]], ICon.ICon[Any, Any, MutableMapping[Any, Any]], dict[tuple[int,int,int],MutableMapping[Any, Any]]]
        for key, value in data.items():
            if key.data == "data":
                additional_data = value
                break
        else:
            raise KeyError("data")
        for layer in range(size_tuple[1]): # for each horizontal slice.
            output.append((0, f"Layer {layer}/{size_tuple[1]}:"))
            output.extend((indentation + 1, line) for indentation, line in self.print_layer(states, additional_data, layer, size_tuple, trace, environment))
        return output

    def compare_text_size(self, size:tuple[Diff.Diff[SCon.SDon[int]],...]) -> list[LineDelegate.LineType]:
        output:list[LineDelegate.LineType] = []
        if any(axis.length > 1 for axis in size):
            old_size = "×".join(str(axis[1] if isinstance(axis, Diff.Diff) else axis) for axis in size)
            new_size = "×".join(str(axis[0] if isinstance(axis, Diff.Diff) else axis) for axis in size)
            output.append((0, f"Changed size from {old_size} to {new_size}"))
        return output

    def compare_text_layer(
            self,
            data:ICon.IDon[Diff.Diff[SCon.SDon[tuple[int,int,int]]], Diff.Diff[SCon.SDon[int]], MutableMapping[tuple[int,int,int], int], SCon.SCon[tuple[int,int,int]], SCon.SCon[int]],
            block_data_comparisons:list[list[LineDelegate.LineType]],
            layer:int,
            size:tuple[int,...],
            trace:Trace.Trace,
            environment:StructureEnvironment.ComparisonEnvironment
        ) -> list[LineDelegate.LineType]:
        output:list[LineDelegate.LineType] = []
        layer_2d = {position.last_value[1]: state for position, state in data.items() if position.last_value == layer}
        old_layer:dict[tuple[int,int,int],int] = {}
        new_layer:dict[tuple[int,int,int],int] = {}
        layers_are_same = True
        for position, state in layer_2d.items():
            if state.length > 1:
                layers_are_same = False
            old_layer[position] = state[0][0]
            new_layer[position] = state[1][1]

        if layers_are_same:
            output.extend(self.print_layer(new_layer, None, layer, size, trace, environment[1]))
        else:
            output.append((0, "Old layer:"))
            output.extend((indentation + 1, line) for indentation, line in self.print_layer(old_layer, None, layer, size, trace, environment[0]))
            output.append((0, "New layer:"))
            output.extend((indentation + 1, line) for indentation, line in self.print_layer(new_layer, None, layer, size, trace, environment[1]))
        for block_data_comparison in block_data_comparisons:
            output.extend(block_data_comparison)
        return output

    def compare_text_block(
        self,
        position:tuple[int,int,int],
        block_data:Diff.Diff[ICon.IDon[Diff.Diff[Any], Diff.Diff[Any], MutableMapping[Any, Any], Any, Any]],
        trace:Trace.Trace,
        environment:StructureEnvironment.ComparisonEnvironment,
    ) -> tuple[list[LineDelegate.LineType],bool]:
        output:list[LineDelegate.LineType] = []
        any_changes:bool
        if block_data.contains_diffs:  # because two total branches are assumed, if this is True, `value_diff` has only one bundle with both branches.
            substructure_output = self.substructure.print_comparison(block_data.last_value, trace, environment)
            if substructure_output is ...:
                return [], False
            self.print_single(None, substructure_output, output, message="Changed ", post_message=f" at {", ".join(map(str, position))}")
            any_changes = True
        elif block_data.length > 1: # if there is a shallow change and both branches 0 and 1 exist.
            substructure_output1 = self.get_item_output(block_data[0].get_con(0), self.substructure, trace, environment[0])
            substructure_output2 = self.get_item_output(block_data[1].get_con(1), self.substructure, trace, environment[1])
            self.print_double(None, substructure_output1, substructure_output2, "Changed", output, post_message=f" at {", ".join(map(str, position))}")
            any_changes = True
        elif not block_data.value_exists_at(0) or not block_data.value_exists_at(1): # addition or removal.
            branch = 1 if block_data.value_exists_at(1) else 0
            message = "Added " if branch == 1 else "Removed "
            substructure_output = self.get_item_output(block_data[branch].get_con(branch), self.substructure, trace, environment[branch])
            self.print_single(None, substructure_output, output, message=message, post_message=f" at {", ".join(map(str, position))}")
            any_changes = True
        else: # no change occured; does not need to be documented.
            any_changes = False
        return output, any_changes

    def print_comparison(self, data: ICon.ICon[Diff.Diff[Con.Don[Any]], Diff.Diff[Any], DataTypedDict], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> list[tuple[int, str]] | EllipsisType:
        data_dict = {key.last_value.last_value: value for key, value in data.items()}
        size_container:ICon.IDon[Diff.Diff[SCon.SDon[int]], Diff.Diff[SCon.SDon[int]], tuple[int,int,int], SCon.SCon[int], SCon.SCon[int]] = data_dict["size"].last_value
        size:tuple[Diff.Diff[SCon.SDon[int]],...] = tuple(value for value in size_container.values())
        states:ICon.IDon[Diff.Diff[SCon.SDon[tuple[int,int,int]]], Diff.Diff[SCon.SDon[int]], MutableMapping[tuple[int,int,int], int], SCon.SCon[tuple[int,int,int]], SCon.SCon[int]] = data_dict["states"].last_value
        additional_data_container:ICon.IDon[ Diff.Diff[SCon.SDon[tuple[int,int,int]]], Diff.Diff[ICon.IDon[Diff.Diff[Any], Diff.Diff[Any], MutableMapping[Any, Any], Any, Any]],
            MutableMapping[tuple[int,int,int], MutableMapping[Any, Any]], SCon.SCon[tuple[int,int,int]], ICon.ICon[Any, Any, MutableMapping[Any, Any]]] = data_dict["data"].last_value
        additional_data:dict[tuple[int,int,int], Diff.Diff[ICon.IDon[Diff.Diff[Any], Diff.Diff[Any], MutableMapping[Any, Any], Any, Any]]] = {key.last_value.last_value: value for key, value in additional_data_container.items()}

        output:list[LineDelegate.LineType] = []
        layers_to_print:set[int] = set()
        size_comparison = self.compare_text_size(size)
        if len(size_comparison) > 0:
            output.extend(size_comparison)

        max_size = tuple(max(size[axis][0][0], size[axis][1][1]) if size[axis].value_exists_at(0) and size[axis].value_exists_at(1) else size[axis].last_value.last_value for axis in range(3))
        block_data_comparisons:list[list[list[LineDelegate.LineType]]] = [[] for i in range(max_size[1])] # top is list for each layer. Second is list for each changed block. Last is Line for each line in comparison.
        for position_diff, state in states.items():
            with trace.enter_key(position_diff, state):
                position = position_diff.last_value.last_value # assume no weird diffiness.

                block_data = additional_data.get(position)
                if block_data is not None:
                    block_data_comparison, block_data_has_changes = self.compare_text_block(position, block_data, trace, environment)
                    if block_data_has_changes:
                        block_data_comparisons[position[1]].append(block_data_comparison)
                else:
                    block_data_comparison = None
                    block_data_has_changes = False

                if isinstance(state, Diff.Diff) or block_data_has_changes:
                    layers_to_print.add(position[1])

        for layer in sorted(layers_to_print):
            with trace.enter_key(f"layer {layer}", layer):
                output.append((0, f"Changed layer {layer}/{max_size[1]}:"))
                output.extend(self.compare_text_layer(states, block_data_comparisons[layer], layer, max_size, trace, environment))
        return output
