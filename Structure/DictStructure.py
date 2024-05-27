from typing import Any, Callable, Generator, Iterable, Literal, MutableMapping, TypeVar

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureSet as StructureSet
import Structure.StructureUtilities as SU
import Structure.Trace as Trace
import Utilities.Nbt.NbtTypes as NbtTypes
import Utilities.TypeVerifier as TypeVerifier

b = TypeVar("b")
d = TypeVar("d")

def infinite_generator(item:d) -> Generator[d,None,None]:
    '''A generator that returns the same value forever.'''
    while True:
        yield item

def glue_iterables(iter1:Iterable[b], iter2:Iterable[d]) -> Generator[b|d,None,None]:
    yield from iter1
    yield from iter2

class DictStructure(Structure.Structure[MutableMapping[str, d]]):

    valid_types = (dict, NbtTypes.TAG_Compound)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("structure", "a Structure, None, or a dict", True, TypeVerifier.UnionTypeVerifier("a Structure, None, or a dict",
            Structure.Structure,
            type(None),
            TypeVerifier.DictTypeVerifier(dict, type, (Structure.Structure, type(None)), "a dict", "a type", "a Structure or None")
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a tuple", True, TypeVerifier.ListTypeVerifier(type, tuple, "a type", "a tuple")),
        TypeVerifier.TypedDictKeyTypeVerifier("detect_key_moves", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("comparison_move_function", "a Callable or None", True, (Callable, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a list", True, TypeVerifier.ListTypeVerifier(Normalizer.Normalizer, list, "a Normalizer", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("children_has_normalizer", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("children_tags", "a set", True, TypeVerifier.IterableTypeVerifier(str, set, "a str", "a set")),
    )

    def __init__(
            self,
            name:str,
            field:str,
            structure:Structure.Structure[d]|None|dict[type,Structure.Structure[d]|None],
            types:tuple[type,...]|None,
            detect_key_moves:bool,
            comparison_move_function:Callable[[str, d], Any]|None,
            measure_length:bool,
            print_all:bool,
            normalizer:list[Normalizer.Normalizer],
            tags:list[str],
            children_has_normalizer:bool,
            children_tags:set[str],
        ) -> None:
        ''' * `name` is what the key of this dictionary is.
         * If `structure` is a Structure, then it will compare and print all values using that Structure.
         * If `structure` is None, then it will use `stringify` in place of a printer and not compare.
         * If `structure` is a dictionary with keys of tuples of types and values of Structure or Nones, then it will use the type of each value to choose the Structure.
         * `types` is a tuple of types. All values of this dictionary must be one of those types.
         * `detect_key_moves` controls whether it will look for changes in keys.
         * `comparison_move_function` is called with a key and value, and returns a piece of the value. It is used to compare the change in keys between two data.
         * If `comparison_move_function` returns None, then it will not attempt to detect moves for that value.
         * If `measure_length` is True, then it will show how the length of the data changed when comparing.
         * If `print_all` is True, then if there is a change in one part of the data, then all parts will be printed.
         * `normalizer` is a list of normalizer functions that modify the data without returning anything.'''
        super().__init__(name, field, normalizer, children_has_normalizer, children_tags)

        self.structure = structure
        self.types = (object,) if types is None else types
        self.detect_key_moves = detect_key_moves
        self.comparison_move_function = (lambda key, value: value) if comparison_move_function is None else comparison_move_function
        self.measure_length = measure_length
        self.print_all = print_all
        self.tags = tags

    def check_initialization_parameters(self) -> None:
        self.type_verifier.base_verify({
            "name": self.name,
            "field": self.field,
            "structure": self.structure,
            "types": self.types,
            "detect_key_moves": self.detect_key_moves,
            "comparison_move_function": self.comparison_move_function,
            "measure_length": self.measure_length,
            "print_all": self.print_all,
            "normalizer": self.normalizer,
            "tags": self.tags,
            "children_has_normalizer": self.children_has_normalizer,
            "children_tags": self.children_tags,
        })

    def iter_structures(self) -> Iterable[Structure.Structure]:
        if self.structure is None: return []
        elif isinstance(self.structure, dict): return (substructure for substructure in self.structure.values() if substructure is not None)
        else: return [self.structure]

    def check_type(self, key:str, value:d) -> Trace.ErrorTrace|None:
        if isinstance(key, D.Diff) or isinstance(value, D.Diff):
            raise TypeError("`check_type` was given data containing Diffs!")
        if not isinstance(value, self.types):
            return Trace.ErrorTrace(TypeError("Key, value %s: %s in %s excepted because value is not %s!" % (SU.stringify(key), SU.stringify(value), self.name, self.types)), self.name, key, value)

    def check_all_types(self, data:MutableMapping[str,d], environment:StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        '''Recursively checks if the types are correct. Should not be given data containing Diffs.'''
        output:list[Trace.ErrorTrace] = []
        if not isinstance(data, self.valid_types):
            output.append(Trace.ErrorTrace(TypeError("`data` has the wrong type, %s instead of [%s]!" % (type(data), ", ".join(valid_type.__name__ for valid_type in self.valid_types))), self.name, None, data))
            return output
        for key, value in data.items():
            check_type_output = self.check_type(key, value)
            if check_type_output is not None:
                output.append(check_type_output)
                continue

            structure, new_exceptions = self.choose_structure_flat(key, type(value), value)
            for exception in new_exceptions: exception.add(self.name, key)
            output.extend(new_exceptions)
            if structure is not None:
                new_exceptions = structure.check_all_types(value, environment)
                for exception in new_exceptions: exception.add(self.name, key)
                output.extend(new_exceptions)
        return output

    def normalize(self, data:dict[str,d], normalizer_dependencies:Normalizer.LocalNormalizerDependencies, version_number:int, environment:StructureEnvironment.StructureEnvironment) -> tuple[Any|None,list[Trace.ErrorTrace]]:
        if not self.children_has_normalizer: return None, []
        for normalizer in self.normalizer:
            try:
                normalizer(data, normalizer_dependencies, version_number)
            except Exception as e:
                return None, [Trace.ErrorTrace(e, self.name, None, data)]
        exceptions:list[Trace.ErrorTrace] = []
        for key, value in data.items():
            structure, new_exceptions = self.choose_structure_flat(key, type(value), value)
            for exception in new_exceptions: exception.add(self.name, key)
            exceptions.extend(new_exceptions)
            if structure is not None:
                normalizer_output, new_exceptions = structure.normalize(value, normalizer_dependencies, version_number, environment)
                for exception in new_exceptions: exception.add(self.name, key)
                exceptions.extend(new_exceptions)
                if normalizer_output is not None:
                    data[key] = normalizer_output
        return None, exceptions

    def get_tag_paths(self, data: MutableMapping[str, d], tag: str, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        output:list[DataPath.DataPath] = []
        if tag in self.tags:
            output.extend(data_path.copy((key, type(value))).embed(value) for key, value in data.items())
        exceptions:list[Trace.ErrorTrace] = []
        for key, value in data.items():
            structure, new_exceptions = self.choose_structure_flat(key, type(value), value)
            for exception in new_exceptions: exception.add(self.name, key)
            exceptions.extend(new_exceptions)
            if structure is not None:
                new_tags, new_exceptions = structure.get_tag_paths(value, tag, data_path.copy((key, type(value))), environment)
                output.extend(new_tags)
                for exception in new_exceptions: exception.add(self.name, key)
                exceptions.extend(new_exceptions)
        return output, exceptions

    def compare(
            self,
            data1:MutableMapping[str,d],
            data2:MutableMapping[str,d],
            environment:StructureEnvironment.StructureEnvironment,
        ) -> tuple[MutableMapping[str|D.Diff[str,str],d|D.Diff[d,d]],bool,list[Trace.ErrorTrace]]:
        if type(data1) != type(data2):
            raise TypeError("Attempted to compare type %s with type %s!" % (data1.__class__.__name__, data2.__class__.__name__))

        if data1 is data2 or data1 == data2:
            return data1, False, [] # type: ignore

        has_changes = False
        key_occurrences:dict[str,list[D.DiffType]] = {}
        exceptions:list[Trace.ErrorTrace] = []

        # get occurrence counts
        data1_iterator = zip(infinite_generator(D.DiffType.old), data1.items()) # since zip stops at the shortest iterator, this will not run forever.
        data2_iterator = zip(infinite_generator(D.DiffType.new), data2.items())
        for diff_type, (key, value) in glue_iterables(data1_iterator, data2_iterator):
            if (check_type_exception := self.check_type(key, value)) is not None:
                exceptions.append(check_type_exception)
            if key in key_occurrences:
                key_occurrences[key].append(diff_type)
            else:
                key_occurrences[key] = [diff_type]

        data_for_add_remove_change_compare:dict[str|D.Diff[str,str],tuple[tuple[D.DiffType, d],...]] = {}
        # assemble key change dicts.
        old_comparison_values:list[tuple[str,d]] = []
        new_comparison_values:list[tuple[str,d]] = []
        for key, occurrences in key_occurrences.items():
            if len(occurrences) == 1:
                match self.detect_key_moves, occurrences[0]:
                    case True, D.DiffType.old:
                        comparison_move_function_return = self.comparison_move_function(key, data1[key])
                        # If `comparison_move_function_return` is None, do not detect key change.
                        if comparison_move_function_return is None: data_for_add_remove_change_compare[key] = ((D.DiffType.old, data1[key]),)
                        else: old_comparison_values.append((key, comparison_move_function_return))
                    case True, D.DiffType.new:
                        comparison_move_function_return = self.comparison_move_function(key, data2[key])
                        if comparison_move_function_return is None: data_for_add_remove_change_compare[key] = ((D.DiffType.new, data2[key]),)
                        else: new_comparison_values.append((key, comparison_move_function_return))
                    case False, D.DiffType.old:
                        data_for_add_remove_change_compare[key] = ((D.DiffType.old, data1[key]),)
                    case False, D.DiffType.new:
                        data_for_add_remove_change_compare[key] = ((D.DiffType.new, data2[key]),)
            elif len(occurrences) == 2:
                data_for_add_remove_change_compare[key] = ((D.DiffType.old, data1[key]), (D.DiffType.new, data2[key]))
            else:
                raise RuntimeError("Illegal state!")

        if self.detect_key_moves: # if False, then additions and removals are added to data_for_add_remove_change_compare above.
            # find matching values.
            new_keys_involved_in_key_change:set[str] = set()
            for old_key, old_comparison_value in old_comparison_values:
                for new_key, new_comparison_value in new_comparison_values:
                    if new_key in new_keys_involved_in_key_change: continue # to prevent multiple things moving to the same place.
                    # old_key cannot equal new_key
                    if old_comparison_value == new_comparison_value:
                        key_diff = D.Diff(old_key, new_key)
                        data_for_add_remove_change_compare[key_diff] = ((D.DiffType.old, data1[old_key]), (D.DiffType.new, data2[new_key]))
                        new_keys_involved_in_key_change.add(new_key)
                        break
                else: # when this old_key's comparison value has no matching new_key's comparison value; when this old key has no corresponding new key whatsoever.
                    data_for_add_remove_change_compare[old_key] = ((D.DiffType.old, data1[old_key]),)
            # find new keys that are not involved in a key move so they can be documented as additions.
            for new_key, new_comparison_value in new_comparison_values:
                if new_key in new_keys_involved_in_key_change: continue
                data_for_add_remove_change_compare[new_key] = ((D.DiffType.new, data2[new_key]),)

        output:dict[str|D.Diff,d|D.Diff] = {}
        for key, occurrences in data_for_add_remove_change_compare.items():
            if len(occurrences) == 2:
                value1, value2 = occurrences[0][1], occurrences[1][1]
                if value1 is value2 or value1 == value2:
                    # no change occurred, so nothing needs to be done whatsoever on this data. If the previous, identical data was
                    # verified, then this would be correct data too.
                    output[key] = value1
                else:
                    structure_set, new_exceptions = self.choose_structure(key, D.Diff(value1, value2))
                    for exception in new_exceptions: exception.add(self.name, D.first_existing_property(key))
                    exceptions.extend(new_exceptions)
                    output[key], subcomponent_has_changes, new_exceptions = structure_set.compare(value1, value2, environment)
                    has_changes = has_changes or subcomponent_has_changes
                    for exception in new_exceptions: exception.add(self.name, D.first_existing_property(key))
                    exceptions.extend(new_exceptions)
                    continue
            elif len(occurrences) == 1:
                # since there's now only one value, there's no more comparing to do.
                # key can only be a D.Diff when len(occurrences) == 2
                assert not isinstance(key, D.Diff)
                if occurrences[0][0] == D.DiffType.old: diff_key, diff_value = D.Diff(old=key), D.Diff(old=occurrences[0][1])
                elif occurrences[0][0] == D.DiffType.new: diff_key, diff_value = D.Diff(new=key), D.Diff(new=occurrences[0][1])
                else: raise RuntimeError("Illegal state!")
                has_changes = True
                output[diff_key] = diff_value
                continue
            else:
                raise RuntimeError("Illegal state: %s, %s" % (key, occurrences))

        sorted_output:dict[str|D.Diff,d|D.Diff] = type(data1)() # type: ignore # why does it even error anyways
        for key, value in sorted(output.items()):
            sorted_output[key] = value
        return sorted_output, has_changes, exceptions

    def choose_structure_flat(self, key:str, value_type: type[d], value:d|None) -> tuple[Structure.Structure|None, list[Trace.ErrorTrace]]:
        if isinstance(self.structure, dict):
            output:Structure.Structure[d]|None|Literal[Structure.StructureFailure.choose_structure_failure] = self.structure.get(value_type, Structure.StructureFailure.choose_structure_failure)
            if output is Structure.StructureFailure.choose_structure_failure:
                return None, [Trace.ErrorTrace(KeyError("Failed to get Structure of key, value: %s: %s" % (key, value_type)), self.name, key, value)]
            return output, []
        else:
            return self.structure, []

    def choose_structure(self, key:str|D.Diff[str,str], value:d|D.Diff[d,d]) -> tuple[StructureSet.StructureSet, list[Trace.ErrorTrace]]:
        output:dict[D.DiffType,Structure.Structure|None] = {}
        exceptions:list[Trace.ErrorTrace] = []
        for value_iter, value_diff_type in D.iter_diff(value):
            if isinstance(self.structure, dict):
                structure = self.structure.get(type(value_iter), Structure.StructureFailure.choose_structure_failure)
                if structure is Structure.StructureFailure.choose_structure_failure:
                    exceptions.append(Trace.ErrorTrace(KeyError("Failed to get Structure of key, value: %s: %s" % (key, value)), self.name, D.first_existing_property(key), value_iter))
                    continue
                    # errors might not be caught by the type checker.
                output[value_diff_type] = structure
            else:
                output[value_diff_type] = self.structure
        return StructureSet.StructureSet(output), exceptions

    def print_item(self, key:str, value:d, structure_set:StructureSet.StructureSet[d], environment:StructureEnvironment.StructureEnvironment, *,message:str="") -> tuple[list[SU.Line],list[Trace.ErrorTrace]]:
        substructure_output, exceptions = structure_set.print_text(D.DiffType.not_diff, value, environment)
        match len(substructure_output):
            case 0:
                return [SU.Line("%s%s %s: empty") % (message, self.field, SU.stringify(key))], exceptions
            case 1:
                return [SU.Line("%s%s %s: %s") % (message, self.field, SU.stringify(key), substructure_output[0])], exceptions
            case _:
                output:list[SU.Line] = []
                output.append(SU.Line("%s%s %s:") % (message, self.field, SU.stringify(key)))
                output.extend(line.indent() for line in substructure_output)
                return output, exceptions

    def print_text(self, data:MutableMapping[str, d], environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line], list[Trace.ErrorTrace]]:
        output:list[SU.Line] = []
        if not isinstance(data, self.valid_types):
            return output, [Trace.ErrorTrace(TypeError("`data` is not [%s], but instead type %s!" % (", ".join(valid_type.__name__ for valid_type in self.valid_types), type(data))), self.name, None, data)]
        exceptions:list[Trace.ErrorTrace] = []
        for key, value in data.items():
            structure_set, new_exceptions = self.choose_structure(key, value)
            for exception in new_exceptions: exception.add(self.name, key)
            exceptions.extend(new_exceptions)
            new_lines, new_exceptions = self.print_item(key, value, structure_set, environment)
            output.extend(new_lines)
            for exception in new_exceptions: exception.add(self.name, key)
            exceptions.extend(new_exceptions)
        return output, exceptions

    def compare_text(self, data:MutableMapping[str, d], environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line],bool, list[Trace.ErrorTrace]]:
        output:list[SU.Line] = []
        any_changes = False
        if not isinstance(data, self.valid_types):
            return [], False, [Trace.ErrorTrace(TypeError("`data` is not [%s], but instead type %s!" % (", ".join(valid_type.__name__ for valid_type in self.valid_types), type(data))), self.name, None, data)]
        current_length, addition_length, removal_length = 0, 0, 0
        size_changed = False
        exceptions:list[Trace.ErrorTrace] = []
        for key, value in data.items():
            can_print_print_all = True # if the print_all thing is overridden for whatever reason.
            key_str = key.first_existing_property() if isinstance(key, D.Diff) else key
            structure_set, new_exceptions = self.choose_structure(key, value)
            for exception in new_exceptions: exception.add(self.name, key)
            exceptions.extend(new_exceptions)

            if isinstance(key, D.Diff) and key.is_change:
                can_print_print_all = False
                any_changes = True
                output.append(SU.Line("Moved %s %s to %s.") % (self.field, SU.stringify(key.old), SU.stringify(key.new)))
            if isinstance(value, D.Diff):
                any_changes = True
                size_changed = True
                match value.change_type:
                    case D.ChangeType.addition:
                        current_length += 1; addition_length += 1
                        new_exceptions = self.print_single(key_str, value.new, "Added", output, structure_set[D.DiffType.new], environment)
                    case D.ChangeType.change:
                        current_length += 1
                        new_exceptions = self.print_double(key_str, value.old, value.new, "Changed", output, structure_set, environment)
                    case D.ChangeType.removal:
                        removal_length += 1
                        new_exceptions = self.print_single(key_str, value.old, "Removed", output, structure_set[D.DiffType.old], environment)
                for exception in new_exceptions: exception.add(self.name, key)
                exceptions.extend(new_exceptions)
            else:
                current_length += 1
                if structure_set[D.DiffType.not_diff] is None:
                    if self.print_all and can_print_print_all:
                        new_lines, new_exceptions = self.print_item(key_str, value, structure_set, environment, message="Unchanged ")
                        output.extend(new_lines)
                        for exception in new_exceptions: exception.add(self.name, key)
                        exceptions.extend(new_exceptions)
                    pass # This means that it is not a difference and does not contain differences.
                else:
                    substructure_output, has_changes, new_exceptions = structure_set.compare_text(D.DiffType.not_diff, value, environment)
                    for exception in new_exceptions: exception.add(self.name, key)
                    exceptions.extend(new_exceptions)
                    if has_changes:
                        any_changes = True
                        output.append(SU.Line("Changed %s %s:") % (self.field, SU.stringify(key_str)))
                        output.extend(line.indent() for line in substructure_output)
                    elif self.print_all and can_print_print_all:
                        new_lines, new_exceptions = self.print_item(key_str, value, structure_set, environment, message="Unchanged ")
                        output.extend(new_lines)
                        for exception in new_exceptions: exception.add(self.name, key)
                        exceptions.extend(new_exceptions)
        if self.measure_length and size_changed:
            output = [SU.Line("Total %s: %i (+%i, -%i)") % (self.field, current_length, addition_length, removal_length)] + output
        return output, any_changes, exceptions
