import math
from typing import (Any, Iterable, Mapping, MutableMapping, MutableSequence,
                    cast)

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureUtilities as SU
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

LAYER_CHARACTERS_DEFAULT = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_-+={[}];:'<,>./?αβγδεζηθικλμνξπρσςτυφχψωΓΔΘΛΞΠΣΦΨΩБбгДдËëЖжЗзИиЙйЛлФфЦцЧчШшЩщЪъЫыЬьЭэЮюЯя" # no such thing as too many letters

class VolumeStructure(Structure.Structure[MutableSequence[MutableMapping[str,Any]]]):

    def __init__(
            self,
            name:str,
            field:str,
            position_key:str,
            state_key:str,
            print_additional_data:bool, # whether to print the extra data like the nbt key in structures_nbt
            children_has_normalizer:bool,
            children_tags:set[str],
            layer_characters:str=LAYER_CHARACTERS_DEFAULT,
        ) -> None:
        super().__init__(name, field, children_has_normalizer, children_tags)

        self.position_key = position_key
        self.state_key = state_key
        self.print_additional_data = print_additional_data
        self.layer_characters = layer_characters

        self.structure:Structure.Structure[MutableMapping[str,Any]]|None = None
        self.normalizer:list[Normalizer.Normalizer]|None = None
        self.tags:list[str]|None = None

    def link_substructures(
        self,
        structure:Structure.Structure[MutableMapping[str,Any]]|None,
        normalizer:list[Normalizer.Normalizer],
        tags:list[str]
    ) -> None:
        self.structure = structure
        self.normalizer = normalizer
        self.tags = tags

    def iter_structures(self) -> Iterable[Structure.Structure]:
        if self.structure is None: return []
        else: return [self.structure]

    def check_all_types(self, data:tuple[dict[tuple[int,int,int],int],dict[tuple[int,int,int],dict[str,Any]],tuple[int,int,int]], environment:StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        '''Recursively checks if the types are correct. Should not be given data containing Diffs.'''
        output:list[Trace.ErrorTrace] = []
        # most of this stuff was checked in `normalize`
        for index, (position, additional_data) in enumerate(data[1].items()):
            if self.structure is None:
                if  len(additional_data) > 0:
                    output.append(Trace.ErrorTrace(Exceptions.VolumeStructureUnrecognizedKeysError(list(additional_data.keys())), self.name, index, additional_data))
            else:
                new_exceptions = self.structure.check_all_types(additional_data, environment)
                for exception in new_exceptions: exception.add(self.name, index)
                output.extend(new_exceptions)
        return output

    def normalize_data(self, data:MutableSequence[MutableMapping[str,Any]]) -> tuple[tuple[dict[tuple[int,int,int],int],dict[tuple[int,int,int],dict[str,Any]],tuple[int,int,int]],list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        max_x, max_y, max_z = 0, 0, 0
        states:dict[tuple[int,int,int],int] = {}
        additional_data:dict[tuple[int,int,int],dict[str,Any]] = {}
        for index, block in enumerate(data):
            position_list = block.get(self.position_key, None)
            state = block.get(self.state_key, None)

            if position_list is None:
                exceptions.append(Trace.ErrorTrace(Exceptions.VolumeStructureMissingKeyError("Position", self.position_key, index), self.name, index, block))
                continue
            if state is None:
                exceptions.append(Trace.ErrorTrace(Exceptions.VolumeStructureMissingKeyError("State", self.state_key, index), self.name, index, block))
                continue
            try: # try except because it could be a not-list, which would raise an exception on the tuple() call.
                if len(position_list) != 3:
                    exceptions.append(Trace.ErrorTrace(Exceptions.VolumeStructureInvalidKeyError("Position", position_list, index, "is not length 3"), self.name, index, block))
                    continue
                position:tuple[int,int,int] = cast(tuple[int,int,int], tuple(position_list))
            except Exception:
                exceptions.append(Trace.ErrorTrace(Exceptions.VolumeStructureInvalidKeyError("Position", position_list, index), self.name, index, block))
                continue
            if not all(isinstance(axis, int) for axis in position):
                exceptions.append(Trace.ErrorTrace(Exceptions.VolumeStructureInvalidKeyError("Position", position, index, "has an axis that is not an int"), self.name, index, block))
            if not isinstance(state, int):
                exceptions.append(Trace.ErrorTrace(Exceptions.VolumeStructureInvalidKeyError("State", state, index, "is not an int"), self.name, index, block))
                continue
            weird_axes = [(axis, label) for axis, label in zip(position, "xyz") if axis < 0]
            if len(weird_axes) > 0:
                exceptions.append(Trace.ErrorTrace(Exceptions.VolumeStructureInvalidKeyError("Position", position, index, "has an axis that is less than 0"), self.name, index, block))
                continue
            if state >= len(self.layer_characters):
                exceptions.append(Trace.ErrorTrace(Exceptions.VolumeStructureInvalidKeyError("State", state, index, "is at least %i, the maximum for this VolumeStructure" % (self.layer_characters)), self.name, index, block))

            max_x, max_y, max_z = max(max_x, position[0]), max(max_y, position[1]), max(max_z, position[2])
            states[position] = int(state)
            if len(block) > 2:
                additional_data[position] = {key: value for key, value in block.items() if key != self.position_key and key != self.state_key}
        return (states, additional_data, (max_x + 1, max_y + 1, max_z + 1)), exceptions

    def normalize(
            self,
            data:MutableSequence[MutableMapping[str,Any]],
            environment:StructureEnvironment.StructureEnvironment,
        ) -> tuple[tuple[dict[tuple[int,int,int],int],dict[tuple[int,int,int],dict[str,Any]],tuple[int,int,int]],list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        data_output, new_exceptions = self.normalize_data(data)
        for exception in new_exceptions: exception.add(self.name, None)
        exceptions.extend(new_exceptions)
        if not self.children_has_normalizer: return data_output, []
        if self.normalizer is None:
            raise Exceptions.AttributeNoneError("normalizer", self)
        for normalizer in self.normalizer:
            try:
                normalizer(data_output)
            except Exception as e:
                return data_output, [Trace.ErrorTrace(e, self.name, None, data_output)]
        for index, (coordinate, item) in enumerate(data_output[1].items()):
            if self.structure is not None:
                normalizer_output, new_exceptions = self.structure.normalize(item, environment)
                for exception in new_exceptions: exception.add(self.name, index)
                exceptions.extend(new_exceptions)
                if normalizer_output is not None:
                    data_output[1][coordinate] = normalizer_output
        return data_output, exceptions

    def get_tag_paths(
            self,
            data:tuple[dict[tuple[int,int,int],int],dict[tuple[int,int,int],dict[str,Any]],tuple[int,int,int]],
            tag: str,
            data_path: DataPath.DataPath,
            environment:StructureEnvironment.StructureEnvironment,
        ) -> tuple[list[DataPath.DataPath], list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        output:list[DataPath.DataPath] = []
        exceptions:list[Trace.ErrorTrace] = []
        if self.tags is None:
            raise Exceptions.AttributeNoneError("tags", self)
        block_data = data[1]
        if tag in self.tags:
            output.extend(data_path.copy((position, type(value))).embed(value) for position, value in block_data.items())
        for position, value in block_data.items():
            if self.structure is not None:
                new_tags, new_exceptions = self.structure.get_tag_paths(value, tag, data_path.copy((position, type(value))), environment)
                output.extend(new_tags)
                for exception in new_exceptions: exception.add(self.name, position)
                exceptions.extend(new_exceptions)
        return output, exceptions

    def compare(
            self,
            data1:tuple[dict[tuple[int,int,int],int],dict[tuple[int,int,int],dict[str,Any]],tuple[int,int,int]],
            data2:tuple[dict[tuple[int,int,int],int],dict[tuple[int,int,int],dict[str,Any]],tuple[int,int,int]],
            environment:StructureEnvironment.StructureEnvironment,
        ) -> tuple[
            tuple[
                Mapping[tuple[int,int,int],int|D.Diff[int,int]],
                Mapping[tuple[int,int,int],Mapping[str,Any]|D.Diff[Mapping[str,Any],Mapping[str,Any]]],
                tuple[int|D.Diff[int,int],int|D.Diff[int,int],int|D.Diff[int,int]],
            ],
            bool,
            list[Trace.ErrorTrace],
        ]:
        if data1 is data2 or data1 == data2:
            return data1, False, []
        has_changes = False
        exceptions:list[Trace.ErrorTrace] = []
        states1, additional_data1, size1 = data1
        states2, additional_data2, size2 = data2
        states_output, additional_data_output = {}, {}

        for coordinate1, state1 in states1.items():
            state2 = states2.get(coordinate1)
            if state2 is None:
                has_changes = True
                states_output[coordinate1] = D.Diff(old=state1)
            elif state1 != state2:
                has_changes = True
                states_output[coordinate1] = D.Diff(old=state1, new=state2)
            else:
                states_output[coordinate1] = state1
        for coordinate2, state2 in states2.items():
            state1 = states1.get(coordinate2)
            if state1 is None:
                has_changes = True
                states_output[coordinate2] = D.Diff(new=state2)
            else:
                pass # changes and removals were covered in above code.

        for coordinate1, block_data1 in additional_data1.items():
            if self.structure is None:
                raise Exceptions.AttributeNoneError("structure", self)
            block_data2 = additional_data2.get(coordinate1)
            if block_data2 is None:
                additional_data_output[coordinate1] = D.Diff(old=block_data1)
            elif block_data1 != block_data2:
                additional_data_output[coordinate1], subcomponent_has_changes, new_exceptions = self.structure.compare(block_data1, block_data2, environment)
                has_changes = has_changes or subcomponent_has_changes
                for exception in new_exceptions: exception.add(self.name, coordinate1)
                exceptions.extend(new_exceptions)
            else:
                additional_data_output[coordinate1] = block_data1
        for coordinate2, block_data2 in additional_data2.items():
            block_data1 = additional_data1.get(coordinate2)
            if block_data1 is None:
                additional_data_output[coordinate2] = D.Diff(new=block_data2)
            else:
                pass # changes and removals were covered in above code

        size_output = (
            (size1[0] if size1[0] == size2[0] else D.Diff(size1[0], size2[0])),
            (size1[1] if size1[1] == size2[1] else D.Diff(size1[1], size2[1])),
            (size1[2] if size1[2] == size2[2] else D.Diff(size1[2], size2[2])),
        )

        return (states_output, additional_data_output, size_output), has_changes, exceptions

    def print_item(self, substructure_output:list[SU.Line], position:tuple[int,int,int]) -> list[SU.Line]:
        match len(substructure_output):
            case 0:
                return [SU.Line("%s at (%i, %i, %i): empty") % (self.field, *position)]
            case 1:
                return [SU.Line("%s at (%i, %i, %i): %s" % (self.field, *position, substructure_output[0]))]
            case _:
                output:list[SU.Line] = []
                output.append(SU.Line("%s at (%i, %i, %i):") % (self.field, *position))
                output.extend(line.indent() for line in substructure_output)
                return output

    def print_layer(self, data:dict[tuple[int,int,int],int], additional_data:dict[tuple[int,int,int],dict[str,Any]], layer:int, size:tuple[int,int,int], environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line], list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        layer_2d = [[" " for j in range(size[0])] for i in range(size[2])]
        for x in range(size[0]):
            for z in range(size[2]):
                state = data.get((x, layer, z))
                if state is not None:
                    layer_2d[z][x] = self.layer_characters[state]
        x_axis_size = math.ceil(math.log10(size[0] + 1)) # how tall the horizontal axis is
        z_axis_size = math.ceil(math.log10(size[2] + 1)) # how wide the vertical axis is
        x_labels = [str(i) for i in range(size[0])]
        z_labels = [str(i) for i in range(size[2])]
        for i in range(size[0]):
            x_labels[i] = " " * (x_axis_size - len(x_labels[i])) + x_labels[i]
        for i in range(size[2]):
            z_labels[i] = " " * (z_axis_size - len(z_labels[i])) + z_labels[i]
        output_grid:list[list[str]] = []
        for i in range(x_axis_size):
            output_grid.append(([" "] * (z_axis_size + 1)) + [x_labels[j][i] for j in range(size[0])])
        output_grid.append([])
        for i in range(size[2]):
            output_grid.append(list(z_labels[i] + " ") + layer_2d[i])
        output:list[SU.Line] = [SU.Line("".join(line)) for line in output_grid]
        if self.print_additional_data:
            if len(additional_data) > 0 and self.structure is None:
                exceptions.append(Trace.ErrorTrace(Exceptions.VolumeStructureAdditionalDataError(self), self.name, layer, additional_data))

            if self.structure is not None:
                for position, block_data in additional_data.items():
                    if position[1] != layer: continue
                    substructure_output, new_exceptions = self.structure.print_text(block_data, environment)
                    for exception in new_exceptions: exception.add(self.name, position)
                    exceptions.extend(new_exceptions)
                    output.extend(self.print_item(substructure_output, position))
        return output, exceptions

    def print_text(
            self,
            data:tuple[
                dict[tuple[int,int,int],int],
                dict[tuple[int,int,int],dict[str,Any]],
                tuple[int,int,int]
            ],
            environment:StructureEnvironment.StructureEnvironment,
        ) -> tuple[list[SU.Line], list[Trace.ErrorTrace]]:
        states, additional_data, size = data
        output:list[SU.Line] = []
        exceptions:list[Trace.ErrorTrace] = []
        for layer in range(size[1]):
            output.append(SU.Line("Layer %i/%i:" % (layer, size[1])))
            new_lines, new_exceptions = self.print_layer(states, additional_data, layer, size, environment)
            output.extend(line.indent() for line in new_lines)
            for exception in new_exceptions: exception.add(self.name, layer)
            exceptions.extend(new_exceptions)
        return output, exceptions

    def compare_text_size(self, size:tuple[int|D.Diff[int,int],int|D.Diff[int,int],int|D.Diff[int,int]]) -> tuple[list[SU.Line], bool, list[Trace.ErrorTrace]]:
        output:list[SU.Line] = []
        any_changes = False
        if any(isinstance(axis, D.Diff) for axis in size):
            old_size = "×".join(str(axis.old if isinstance(axis, D.Diff) else axis) for axis in size)
            new_size = "×".join(str(axis.new if isinstance(axis, D.Diff) else axis) for axis in size)
            output.append(SU.Line("Changed size from %s to %s" % (old_size, new_size)))
            any_changes = True
        return output, any_changes, []

    def compare_text_layer(
            self,
            data:dict[tuple[int,int,int],int|D.Diff[int,int]],
            block_data_comparisons:list[list[SU.Line]],
            layer:int, size:tuple[int,int,int],
            environment:StructureEnvironment.StructureEnvironment
        ) -> tuple[list[SU.Line], list[Trace.ErrorTrace]]:
        output:list[SU.Line] = []
        exceptions:list[Trace.ErrorTrace] = []
        layer_2d = {position: state for position, state in data.items() if position[1] == layer}
        old_layer:dict[tuple[int,int,int],int] = {}
        new_layer:dict[tuple[int,int,int],int] = {}
        layers_are_same = True
        for position, state in layer_2d.items():
            if isinstance(state, D.Diff):
                layers_are_same = False
                match state.change_type:
                    case D.ChangeType.addition:
                        new_layer[position] = state.new
                    case D.ChangeType.change:
                        new_layer[position] = state.new
                        old_layer[position] = state.old
                    case D.ChangeType.removal:
                        old_layer[position] = state.old
            else:
                old_layer[position] = state
                new_layer[position] = state

        if layers_are_same:
            new_lines, new_exceptions = self.print_layer(new_layer, {}, layer, size, environment)
            output.extend(new_lines)
            for exception in new_exceptions: exception.add(self.name, None)
            exceptions.extend(new_exceptions)
        else:
            output.append(SU.Line("Old layer:"))
            new_lines, new_exceptions = self.print_layer(old_layer, {}, layer, size, environment)
            output.extend(line.indent() for line in new_lines)
            for exception in new_exceptions: exception.add(self.name, None)
            exceptions.extend(new_exceptions)
            output.append(SU.Line("New layer:"))
            new_lines, new_exceptions = self.print_layer(new_layer, {}, layer, size, environment)
            output.extend(line.indent() for line in new_lines)
            for exception in new_exceptions: exception.add(self.name, None)
            exceptions.extend(new_exceptions)
        for block_data_comparison in block_data_comparisons:
            output.extend(block_data_comparison)
        return output, exceptions

    def compare_text_block(self, position:tuple[int,int,int], block_data:dict[str,Any]|D.Diff[dict[str,Any],dict[str,Any]], environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line],bool,list[Trace.ErrorTrace]]:
        output:list[SU.Line] = []
        exceptions:list[Trace.ErrorTrace] = []
        any_changes = False
        if isinstance(block_data, D.Diff):
            match block_data.change_type:
                case D.ChangeType.addition:
                    new_exceptions = self.print_single(None, cast(Any, block_data.new), "Added", output, cast(Any, self.structure), environment, post_message=" at %i, %i, %i" % position)
                case D.ChangeType.change:
                    new_exceptions = self.print_double(None, cast(Any, block_data.old), cast(Any, block_data.new), "Changed", output, cast(Any, self.structure), environment, post_message=" at %i, %i, %i" % position)
                case D.ChangeType.removal:
                    new_exceptions = self.print_single(None, cast(Any, block_data.old), "Removed", output, cast(Any, self.structure), environment, post_message=" at %i, %i, %i" % position)
            any_changes = True
            for exception in new_exceptions: exception.add(self.name, position)
            exceptions.extend(new_exceptions)
        else:
            if self.structure is None:
                raise Exceptions.AttributeNoneError("structure", self)
            substructure_output, has_changes, new_exceptions = self.structure.compare_text(block_data, environment)
            for exception in new_exceptions: exception.add(self.name, position)
            exceptions.extend(new_exceptions)
            if has_changes:
                any_changes = True
                output.append(SU.Line("Changed %s at %i, %i, %i:") % (self.field, *position))
                output.extend(line.indent() for line in substructure_output)
        return output, any_changes, exceptions

    def compare_text(
            self,
            data:tuple[
                dict[tuple[int,int,int],int|D.Diff[int,int]],
                dict[tuple[int,int,int],dict[str,Any]|D.Diff[dict[str,Any],dict[str,Any]]],
                tuple[int|D.Diff[int,int],int|D.Diff[int,int],int|D.Diff[int,int]]
            ],
            environment:StructureEnvironment.StructureEnvironment,
        ) -> tuple[list[SU.Line], bool, list[Trace.ErrorTrace]]:
        states, additional_data, size = data
        output:list[SU.Line] = []
        exceptions:list[Trace.ErrorTrace] = []
        any_changes = False
        layers_to_print:set[int] = set()

        size_comparison, has_changes, new_exceptions = self.compare_text_size(size)
        any_changes = any_changes or has_changes
        for exception in new_exceptions: exception.add(self.name, None)
        exceptions.extend(new_exceptions)
        if len(size_comparison) > 0:
            output.extend(size_comparison)

        max_size:tuple[int,int,int] = tuple((max(axis.old, axis.new) if isinstance(axis, D.Diff) else axis) for axis in size) # type: ignore
        block_data_comparisons:list[list[list[SU.Line]]] = [[] for i in range(max_size[1])] # top is list for each layer. Second is list for each changed block. Last is Line for each line in comparison.
        for position, state in states.items():

            block_data = additional_data.get(position)
            if block_data is not None:
                if self.structure is None:
                    raise Exceptions.AttributeNoneError("structure", self)
                block_data_comparison, block_data_has_changes, new_exceptions = self.compare_text_block(position, block_data, environment)
                if block_data_has_changes:
                    block_data_comparisons[position[1]].append(block_data_comparison)
                for exception in new_exceptions: exception.add(self.name, position)
                exceptions.extend(new_exceptions)
            else:
                block_data_comparison = None
                block_data_has_changes = False

            if isinstance(state, D.Diff) or block_data_has_changes:
                any_changes = True
                layers_to_print.add(position[1])

        for layer in sorted(layers_to_print):
            output.append(SU.Line("Changed layer %i/%i:" % (layer, max_size[1])))
            new_lines, new_exceptions = self.compare_text_layer(states, block_data_comparisons[layer], layer, max_size, environment)
            for exception in new_exceptions: exception.add(self.name, layer)
            exceptions.extend(new_exceptions)
            output.extend(line.indent() for line in new_lines)
        return output, any_changes, exceptions
