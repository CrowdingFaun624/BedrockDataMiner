from typing import Any, Callable, MutableMapping, TypeVar, cast

import Structure.Difference as D
import Structure.Hashing as Hashing
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureSet as StructureSet
import Structure.StructureUtilities as SU
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions
import Utilities.Nbt.NbtTypes as NbtTypes

d = TypeVar("d")

class AbstractMappingStructure(Structure.Structure[MutableMapping[str, d]]):
    """
    Abstract class of dict-using Structures.
    In subclasses, must provide methods `iter_structures`, `check_type`,
    `get_structure`, `choose_structure`, `get_tag_paths`, and `normalize`.
    """

    valid_types = (dict, NbtTypes.TAG_Compound)

    def __init__(
            self,
            name:str,
            field:str,
            detect_key_moves:bool,
            comparison_move_function:Callable[[str, d], Any]|None,
            measure_length:bool,
            print_all:bool,
            sorting_function:Callable[[tuple[str|D.Diff,Any]],Any]|None,
            min_key_similarity_threshold:float,
            min_value_similarity_threshold:float,
            children_has_normalizer:bool,
            children_tags:set[str],
        ) -> None:
        super().__init__(name, field, children_has_normalizer, children_tags)

        self.detect_key_moves = detect_key_moves
        self.comparison_move_function = (lambda key, value: value) if comparison_move_function is None else comparison_move_function
        self.measure_length = measure_length
        self.print_all = print_all
        self.sorting_function = sorting_function
        self.min_key_similarity_threshold = min_key_similarity_threshold
        self.min_value_similarity_threshold = min_value_similarity_threshold

        self.normalizer:list[Normalizer.Normalizer]|None = None
        self.tags:list[str]|None = None

    def link_substructures(
        self,
        normalizer:list[Normalizer.Normalizer],
        tags:list[str],
    ) -> None:
        self.normalizer = normalizer
        self.tags = tags

    def check_type(self, key:str, value:d) -> Trace.ErrorTrace|None: ...

    def get_structure(self, key:str, value:d) -> tuple[Structure.Structure[d]|None, list[Trace.ErrorTrace]]:
        '''
        Returns a substructure or None.
        :The key of this Structure at the current position.
        :value: The value at the current position.
        '''
        ...

    def choose_structure(self, key:str|D.Diff[str,str], value:d|D.Diff[d,d]) -> tuple[StructureSet.StructureSet, list[Trace.ErrorTrace]]: ...

    def check_all_types(self, data:MutableMapping[str,d], environment:StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        '''Recursively checks if the types are correct. Should not be given data containing Diffs.'''
        output:list[Trace.ErrorTrace] = []
        if not isinstance(data, self.valid_types):
            output.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.valid_types, type(data), "Data"), self.name, None, data))
            return output
        for key, value in data.items():
            if (check_type_output := self.check_type(key, value)) is not None:
                output.append(check_type_output)
                continue

            structure, new_exceptions = self.get_structure(key, value)
            output.extend(exception.add(self.name, key) for exception in new_exceptions)
            if structure is not None:
                output.extend(exception.add(self.name, key) for exception in structure.check_all_types(value, environment))
        return output

    def get_similarity(self, data1: MutableMapping[str, d], data2: MutableMapping[str, d]) -> float:
        data1_hashes:dict[int,tuple[str,d]] = {Hashing.hash_data((key, value)): (key, value) for key, value in data1.items()}
        data2_hashes:dict[int,tuple[str,d]] = {Hashing.hash_data((key, value)): (key, value) for key, value in data2.items()}

        same_keys = data1.keys() & data2.keys() # keys present in both old and new data.
        same_hashes = data1_hashes.keys() & data2_hashes.keys()
        data1_exclusive_items = {exclusive_hash: data1_hashes[exclusive_hash] for exclusive_hash in data1_hashes.keys() - data2_hashes.keys()}
        data2_exclusive_items = {exclusive_hash: data2_hashes[exclusive_hash] for exclusive_hash in data2_hashes.keys() - data1_hashes.keys()}
        maximum_length = max(len(data1), len(data2))

        similarity = len(same_hashes) / maximum_length
        if len(data1_exclusive_items) > 0 and len(data2_exclusive_items) > 0:
            already_data1_hashes:set[int] = set() # items of data1_hashes that have already been picked.
            already_data2_hashes:set[int] = set() # items of data2_hashes that have already been picked.
            for hash1, hash2, key_similarity, value_similarity in self.get_similarities_list(data1_exclusive_items, data2_exclusive_items, same_keys):
                if hash1 in already_data1_hashes or hash2 in already_data2_hashes:
                    continue
                already_data1_hashes.add(hash1)
                already_data2_hashes.add(hash2)
                similarity += (key_similarity * (1 - self.min_key_similarity_threshold) + value_similarity * (1 - self.min_value_similarity_threshold)) / (key_similarity + value_similarity) / (2 * maximum_length)
        if similarity < 0.0 or similarity > 1.0:
            raise Exceptions.InvalidSimilarityError(self, similarity, data1, data2)
        return similarity

    def get_key_similarity(self, key1:str, key2:str) -> float:
        '''
        Gets the similarity between two keys of this Structure's data.
        :key1: The key of the older key-value pair.
        :key2: The key of the newer key-value pair.
        '''
        return float(key1 == key2)

    def get_value_similarity(self, key1:str, value1:d, key2:str, value2:d) -> float:
        '''
        Gets the similarity between two values of this Structure's data.
        :key1: The key of the older key-value pair.
        :value1: The value of the older key-value pair.
        :key2: The key of the newer key-value pair.
        :value2: The value of the newer key-value pair.
        '''
        if value1 == value2:
            return 1.0
        structure1, exceptions1 = self.get_structure(key1, value1)
        structure2, exceptions2 = self.get_structure(key2, value2)
        if len(exceptions1) > 0 or len(exceptions2) > 0:
            raise Exceptions.StructureExceptionError(self, self.get_value_similarity, exceptions1 + exceptions2)
        if structure1 is structure2 and structure1 is not None:
            output = structure1.get_similarity(value1, value2)
            return output
        else:
            return 0.0

    def get_similarities_list(self, data1_exclusive_items:dict[int,tuple[str,d]], data2_exclusive_items:dict[int,tuple[str,d]], same_keys:set[str]) -> list[tuple[int,int,float,float]]:
        keys1_hashes = {key1: hash1 for hash1, (key1, value1) in data1_exclusive_items.items()}
        keys2_hashes = {key2: hash2 for hash2, (key2, value2) in data2_exclusive_items.items()}
        same_keys_list:list[tuple[int, int, float, float]] = [
            (keys1_hashes[key], keys2_hashes[key], 1.0, 1.0)
            for key in same_keys
            if key in keys1_hashes # same_keys has all keys that are similar, not just ones with different values.
        ]
        similarities_list:list[tuple[int, int, float, float]] = [ # maps similarity of older items to newer items
            (hash1, hash2, key_similarity, value_similarity)
            for hash1, (key1, value1) in data1_exclusive_items.items()
            if key1 not in same_keys
            for hash2, (key2, value2) in data2_exclusive_items.items()
            if key2 not in same_keys # key1 cannot equal key2
            if all([ # if the keys match or it's acceptable to move them.
                self.detect_key_moves,
                not (key1 in same_keys or key2 in same_keys), # prevent keys present in both old and new from moving.
                (key_similarity := self.get_key_similarity(key1, key2)) >= self.min_key_similarity_threshold,
                (value_similarity := self.get_value_similarity(key1, value1, key2, value2)) > self.min_value_similarity_threshold,
            ])
        ]
        output = same_keys_list + similarities_list
        # sort by weighted similarities using the thresholds.
        output.sort(key=lambda item: item[2] * (1 - self.min_key_similarity_threshold) + item[3] * (1 - self.min_value_similarity_threshold), reverse=True)
        return output

    def compare(
            self,
            data1:MutableMapping[str,d],
            data2:MutableMapping[str,d],
            environment:StructureEnvironment.StructureEnvironment,
        ) -> tuple[MutableMapping[str|D.Diff[str,str],d|D.Diff[d,d]],bool,list[Trace.ErrorTrace]]:

        if data1 is data2 or data1 == data2:
            return cast(Any, data1), False, []
        exceptions:list[Trace.ErrorTrace] = []

        data1_hashes:dict[int,tuple[str,d]] = {Hashing.hash_data((key, value)): (key, value) for key, value in data1.items()}
        data2_hashes:dict[int,tuple[str,d]] = {Hashing.hash_data((key, value)): (key, value) for key, value in data2.items()}

        same_keys = data1.keys() & data2.keys() # keys that existed both before and after.
        same_hashes = data1_hashes.keys() & data2_hashes.keys()
        data1_exclusive_items = {exclusive_hash: data1_hashes[exclusive_hash] for exclusive_hash in data1_hashes.keys() - data2_hashes.keys()}
        data2_exclusive_items = {exclusive_hash: data2_hashes[exclusive_hash] for exclusive_hash in data2_hashes.keys() - data1_hashes.keys()}
        output:dict[str|D.Diff,d|D.Diff] = cast(Any, type(data1)())
        has_changes = len(data1_exclusive_items) > 0 or len(data2_exclusive_items) > 0

        # unchanged items
        for same_hash in same_hashes:
            key, value = data1_hashes[same_hash]
            output[key] = value

        # changed items
        already_data1_hashes:set[int] = set() # items of data1_hashes that have already been picked.
        already_data2_hashes:set[int] = set() # items of data2_hashes that have already been picked.
        if len(data1_exclusive_items) > 0 and len(data2_exclusive_items) > 0:
            for hash1, hash2, key_similarity, value_similarity in self.get_similarities_list(data1_exclusive_items, data2_exclusive_items, same_keys):
                if hash1 in already_data1_hashes or hash2 in already_data2_hashes:
                    continue # if either side is already involved in a change, it's unneeded.
                already_data1_hashes.add(hash1)
                already_data2_hashes.add(hash2)
                key1, value1 = data1_exclusive_items[hash1]
                key2, value2 = data2_exclusive_items[hash2]
                structure1, new_exceptions = self.get_structure(key1, value1)
                exceptions.extend(exception.add(self.name, key1) for exception in new_exceptions)
                structure2, new_exceptions = self.get_structure(key2, value2)
                exceptions.extend(exception.add(self.name, key2) for exception in new_exceptions)
                if self.name == "textures":
                    if key1 != key2:
                        print(key1, key2)
                if key1 == key2:
                    key_compare_output = key1
                else:
                    key_compare_output = D.Diff(key1, key2)
                if value1 is value2 or value1 == value2:
                    value_compare_output = value1
                elif structure1 is not structure2 or structure1 is None:
                    value_compare_output = D.Diff(value1, value2)
                else:
                    value_compare_output, _, new_exceptions = structure1.compare(value1, value2, environment)
                    exceptions.extend(exception.add(self.name, key2) for exception in new_exceptions)
                output[key_compare_output] = value_compare_output

        # added/removed items
        output.update(
            (D.Diff(old=key), D.Diff(old=value))
            for exclusive_hash, (key, value) in data1_exclusive_items.items()
            if exclusive_hash not in already_data1_hashes
        )
        output.update(
            (D.Diff(new=key), D.Diff(new=value))
            for exclusive_hash, (key, value) in data2_exclusive_items.items()
            if exclusive_hash not in already_data2_hashes
        )
        if self.sorting_function is not None:
            output_copy:dict[str|D.Diff,d|D.Diff] = cast(Any, type(output)())
            output_copy.update((key, value) for key, value in sorted(output.items(), key=self.sorting_function))
            output = output_copy
        return output, has_changes, exceptions

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
            return output, [Trace.ErrorTrace(Exceptions.StructureTypeError(self.valid_types, type(data), "Data"), self.name, None, data)]
        exceptions:list[Trace.ErrorTrace] = []
        for key, value in data.items():
            structure_set, new_exceptions = self.choose_structure(key, value)
            exceptions.extend(exception.add(self.name, key) for exception in new_exceptions)
            new_lines, new_exceptions = self.print_item(key, value, structure_set, environment)
            output.extend(new_lines)
            exceptions.extend(exception.add(self.name, key) for exception in new_exceptions)
        return output, exceptions

    def compare_text(self, data:MutableMapping[str, d], environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line],bool, list[Trace.ErrorTrace]]:
        output:list[SU.Line] = []
        any_changes = False
        if not isinstance(data, self.valid_types):
            return [], False, [Trace.ErrorTrace(Exceptions.StructureTypeError(self.valid_types, type(data), "Data"), self.name, None, data)]
        current_length, addition_length, removal_length = 0, 0, 0
        size_changed = False
        exceptions:list[Trace.ErrorTrace] = []
        for key, value in data.items():
            can_print_print_all = True # if the print_all thing is overridden for whatever reason.
            key_str = key.first_existing_property() if isinstance(key, D.Diff) else key
            structure_set, new_exceptions = self.choose_structure(key, value)
            exceptions.extend(exception.add(self.name, key) for exception in new_exceptions)

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
                exceptions.extend(exception.add(self.name, key) for exception in new_exceptions)
            else:
                current_length += 1
                if structure_set[D.DiffType.not_diff] is None:
                    if self.print_all and can_print_print_all:
                        new_lines, new_exceptions = self.print_item(key_str, value, structure_set, environment, message="Unchanged ")
                        output.extend(new_lines)
                        exceptions.extend(exception.add(self.name, key) for exception in new_exceptions)
                    pass # This means that it is not a difference and does not contain differences.
                else:
                    substructure_output, has_changes, new_exceptions = structure_set.compare_text(D.DiffType.not_diff, value, environment)
                    exceptions.extend(exception.add(self.name, key) for exception in new_exceptions)
                    if has_changes:
                        any_changes = True
                        output.append(SU.Line("Changed %s %s:") % (self.field, SU.stringify(key_str)))
                        output.extend(line.indent() for line in substructure_output)
                    elif self.print_all and can_print_print_all:
                        new_lines, new_exceptions = self.print_item(key_str, value, structure_set, environment, message="Unchanged ")
                        output.extend(new_lines)
                        exceptions.extend(exception.add(self.name, key) for exception in new_exceptions)
        if self.measure_length and size_changed:
            output = [SU.Line("Total %s: %i (+%i, -%i)") % (self.field, current_length, addition_length, removal_length)] + output
        return output, any_changes, exceptions
