import math
from typing import Any, Iterator, MutableMapping, TypedDict, TypeVar, cast

import Structure.AbstractMappingStructure as AbstractMappingStructure
import Structure.Delegate.DefaultDelegate as DefaultDelegate
import Structure.DictStructure as DictStructure
import Structure.Difference as D
import Structure.KeymapStructure as KeymapStructure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

a = TypeVar("a")

LAYER_CHARACTERS_DEFAULT = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_-+={[}];:'<,>./?αβγδεζηθικλμνξπρσςτυφχψωΓΔΘΛΞΠΣΦΨΩБбгДдËëЖжЗзИиЙйЛлФфЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"

class DataTypedDict(TypedDict):
    states: dict[tuple[int,int,int],int]
    data: dict[tuple[int,int,int],MutableMapping[str,Any]]
    size: tuple[int,int,int]

class DataDiffTypedDict(TypedDict):
    states: dict[tuple[int,int,int]|D.Diff[tuple[int,int,int],tuple[int,int,int]],int|D.Diff[int,int]]
    data: dict[tuple[int,int,int]|D.Diff[tuple[int,int,int],tuple[int,int,int]],MutableMapping[str,Any]|D.Diff[MutableMapping[str,Any],MutableMapping[str,Any]]]
    size: tuple[int|D.Diff[int,int],int|D.Diff[int,int],int|D.Diff[int,int]]

class VolumeDelegate(DefaultDelegate.DefaultDelegate[tuple[int,int,int]]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("layer_characters", "a str", False, str, lambda key, value: (len(value) == len(set(value)), "all characters must be unique")),
        TypeVerifier.TypedDictKeyTypeVerifier("print_additional_data", "a bool", False, bool),
    )
    
    applies_to = (KeymapStructure.KeymapStructure,)

    def __init__(
        self,
        structure:KeymapStructure.KeymapStructure|None,
        keys:dict[str,Any],
        field:str="block",
        layer_characters:str=LAYER_CHARACTERS_DEFAULT,
        print_additional_data:bool=True,
    ) -> None:
        super().__init__(structure, keys)
        self.field = field
        self.layer_characters = layer_characters
        self.print_additional_data = print_additional_data

        self.substructure:AbstractMappingStructure.AbstractMappingStructure[Any]|None = None

    def finalize(self) -> None:
        super().finalize()
        structure, new_exceptions = cast(tuple[DictStructure.DictStructure, list[Trace.ErrorTrace]], cast(KeymapStructure.KeymapStructure, self.get_structure()).get_structure("data", None))
        substructure = structure.structure
        if len(new_exceptions) > 0:
            raise new_exceptions[0].exception
        if substructure is None or not isinstance(substructure, AbstractMappingStructure.AbstractMappingStructure):
            raise TypeError("Substructure of %r is not an AbstractMappingStructure, but instead %r!" % (self, substructure))
        self.substructure = substructure

    def print_item(self, substructure_output:list[DefaultDelegate.Line], position:tuple[int,int,int]) -> list[DefaultDelegate.Line]:
        match len(substructure_output):
            case 0:
                return [DefaultDelegate.Line("%s at (%i, %i, %i): empty") % (self.field, *position)]
            case 1:
                return [DefaultDelegate.Line("%s at (%i, %i, %i): %s" % (self.field, *position, substructure_output[0]))]
            case _:
                output:list[DefaultDelegate.Line] = []
                output.append(DefaultDelegate.Line("%s at (%i, %i, %i):") % (self.field, *position))
                output.extend(line.indent() for line in substructure_output)
                return output

    def print_layer(self, data:dict[tuple[int,int,int],int], additional_data:dict[tuple[int,int,int],MutableMapping[str,Any]], layer:int, size:tuple[int,int,int], environment:StructureEnvironment.PrinterEnvironment) -> tuple[list[DefaultDelegate.Line], list[Trace.ErrorTrace]]:
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
        output:list[DefaultDelegate.Line] = [DefaultDelegate.Line("".join(line)) for line in output_grid]
        if self.print_additional_data:
            if len(additional_data) > 0 and self.substructure is None:
                exceptions.append(Trace.ErrorTrace(Exceptions.VolumeStructureAdditionalDataError(self.get_structure()), self.get_structure().name, layer, additional_data))

            if self.substructure is not None:
                for position, block_data in additional_data.items():
                    if position[1] != layer: continue
                    substructure_output, new_exceptions = self.substructure.print_text(block_data, environment)
                    exceptions.extend(exception.add(self.get_structure().name, position) for exception in new_exceptions)
                    output.extend(self.print_item(substructure_output, position))
        return output, exceptions

    def print_text(
            self,
            data:DataTypedDict,
            environment:StructureEnvironment.PrinterEnvironment,
        ) -> tuple[list[DefaultDelegate.Line], list[Trace.ErrorTrace]]:
        states, additional_data, size = data["states"], data["data"], data["size"]
        output:list[DefaultDelegate.Line] = []
        exceptions:list[Trace.ErrorTrace] = []
        for layer in range(size[1]):
            output.append(DefaultDelegate.Line("Layer %i/%i:" % (layer, size[1])))
            new_lines, new_exceptions = self.print_layer(states, additional_data, layer, size, environment)
            output.extend(line.indent() for line in new_lines)
            exceptions.extend(exception.add(self.get_structure().name, layer) for exception in new_exceptions)
        return output, exceptions

    def compare_text_size(self, size:tuple[int|D.Diff[int,int],int|D.Diff[int,int],int|D.Diff[int,int]]) -> tuple[list[DefaultDelegate.Line], bool, list[Trace.ErrorTrace]]:
        output:list[DefaultDelegate.Line] = []
        any_changes = False
        if any(isinstance(axis, D.Diff) for axis in size):
            old_size = "×".join(str(axis.old if isinstance(axis, D.Diff) else axis) for axis in size)
            new_size = "×".join(str(axis.new if isinstance(axis, D.Diff) else axis) for axis in size)
            output.append(DefaultDelegate.Line("Changed size from %s to %s" % (old_size, new_size)))
            any_changes = True
        return output, any_changes, []

    def compare_text_layer(
            self,
            data:dict[tuple[int,int,int],int|D.Diff[int,int]],
            block_data_comparisons:list[list[DefaultDelegate.Line]],
            layer:int, size:tuple[int,int,int],
            environment:StructureEnvironment.ComparisonEnvironment
        ) -> tuple[list[DefaultDelegate.Line], list[Trace.ErrorTrace]]:
        output:list[DefaultDelegate.Line] = []
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
            new_lines, new_exceptions = self.print_layer(new_layer, {}, layer, size, environment[1])
            output.extend(new_lines)
            exceptions.extend(exception.add(self.get_structure().name, None) for exception in new_exceptions)
        else:
            output.append(DefaultDelegate.Line("Old layer:"))
            new_lines, new_exceptions = self.print_layer(old_layer, {}, layer, size, environment[0])
            output.extend(line.indent() for line in new_lines)
            exceptions.extend(exception.add(self.get_structure().name, None) for exception in new_exceptions)
            output.append(DefaultDelegate.Line("New layer:"))
            new_lines, new_exceptions = self.print_layer(new_layer, {}, layer, size, environment[1])
            output.extend(line.indent() for line in new_lines)
            exceptions.extend(exception.add(self.get_structure().name, None) for exception in new_exceptions)
        for block_data_comparison in block_data_comparisons:
            output.extend(block_data_comparison)
        return output, exceptions

    def compare_text_block(self, position:tuple[int,int,int], block_data:MutableMapping[str,Any]|D.Diff[MutableMapping[str,Any],MutableMapping[str,Any]], environment:StructureEnvironment.ComparisonEnvironment) -> tuple[list[DefaultDelegate.Line],bool,list[Trace.ErrorTrace]]:
        output:list[DefaultDelegate.Line] = []
        exceptions:list[Trace.ErrorTrace] = []
        any_changes = False
        if isinstance(block_data, D.Diff):
            match block_data.change_type:
                case D.ChangeType.addition:
                    new_exceptions = self.print_single(None, cast(Any, block_data.new), "Added", output, cast(Any, self.substructure), environment[1], post_message=" at %i, %i, %i" % position)
                case D.ChangeType.change:
                    new_exceptions = self.print_double(None, cast(Any, block_data.old), cast(Any, block_data.new), "Changed", output, cast(Any, self.substructure), environment, post_message=" at %i, %i, %i" % position)
                case D.ChangeType.removal:
                    new_exceptions = self.print_single(None, cast(Any, block_data.old), "Removed", output, cast(Any, self.substructure), environment[0], post_message=" at %i, %i, %i" % position)
            any_changes = True
            exceptions.extend(exception.add(self.get_structure().name, position) for exception in new_exceptions)
        else:
            if self.substructure is None:
                raise Exceptions.AttributeNoneError("structure", self)
            substructure_output:list[DefaultDelegate.Line]
            substructure_output, has_changes, new_exceptions = self.substructure.compare_text(block_data, environment)
            exceptions.extend(exception.add(self.get_structure().name, position) for exception in new_exceptions)
            if has_changes:
                any_changes = True
                output.append(DefaultDelegate.Line("Changed %s at %i, %i, %i:") % (self.field, *position))
                output.extend(line.indent() for line in substructure_output)
        return output, any_changes, exceptions

    def process_pos_dict(self, data:dict[tuple[int,int,int]|D.Diff[tuple[int,int,int],tuple[int,int,int]],a]) -> Iterator[tuple[tuple[int,int,int],a]]:
        '''
        Yields the items of the data, removing the key from a Diff if it is in a Diff.
        '''
        yield from (
            ((position.first_existing_property() if isinstance(position, D.Diff) else position), state)
            for position, state in data.items()
        )

    def compare_text(
            self,
            data:DataDiffTypedDict,
            environment:StructureEnvironment.ComparisonEnvironment,
        ) -> tuple[list[DefaultDelegate.Line], bool, list[Trace.ErrorTrace]]:
        states, additional_data, size = data["states"], data["data"], data["size"]
        states = dict(self.process_pos_dict(states))
        additional_data = dict(self.process_pos_dict(additional_data))
        output:list[DefaultDelegate.Line] = []
        exceptions:list[Trace.ErrorTrace] = []
        any_changes = False
        layers_to_print:set[int] = set()

        size_comparison, has_changes, new_exceptions = self.compare_text_size(size)
        any_changes = any_changes or has_changes
        exceptions.extend(exception.add(self.get_structure().name, None) for exception in new_exceptions)
        if len(size_comparison) > 0:
            output.extend(size_comparison)

        max_size:tuple[int,int,int] = tuple((max(axis.old, axis.new) if isinstance(axis, D.Diff) else axis) for axis in size) # type: ignore
        block_data_comparisons:list[list[list[DefaultDelegate.Line]]] = [[] for i in range(max_size[1])] # top is list for each layer. Second is list for each changed block. Last is Line for each line in comparison.
        for position, state in states.items():

            block_data = additional_data.get(position)
            if block_data is not None:
                if self.substructure is None:
                    raise Exceptions.AttributeNoneError("structure", self)
                block_data_comparison, block_data_has_changes, new_exceptions = self.compare_text_block(position, block_data, environment)
                if block_data_has_changes:
                    block_data_comparisons[position[1]].append(block_data_comparison)
                exceptions.extend(exception.add(self.get_structure().name, position) for exception in new_exceptions)
            else:
                block_data_comparison = None
                block_data_has_changes = False

            if isinstance(state, D.Diff) or block_data_has_changes:
                any_changes = True
                layers_to_print.add(position[1])

        for layer in sorted(layers_to_print):
            output.append(DefaultDelegate.Line("Changed layer %i/%i:" % (layer, max_size[1])))
            new_lines, new_exceptions = self.compare_text_layer(states, block_data_comparisons[layer], layer, max_size, environment)
            exceptions.extend(exception.add(self.get_structure().name, layer) for exception in new_exceptions)
            output.extend(line.indent() for line in new_lines)
        return output, any_changes, exceptions

