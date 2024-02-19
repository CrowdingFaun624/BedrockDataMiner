from typing import Callable, Generator, Iterable, TypeVar

import Comparison.ComparerSection as ComparerSection
import Comparison.ComparerSet as ComparerSet
import Comparison.ComparisonUtilities as CU
import Comparison.Difference as D
import Comparison.Normalizer as Normalizer
import Comparison.Trace as Trace

b = TypeVar("b")
c = TypeVar("c")
d = TypeVar("d")

def infinite_generator(item:c) -> Generator[c,None,None]:
    '''A generator that returns the same value forever.'''
    while True:
        yield item

def glue_iterables(iter1:Iterable[c], iter2:Iterable[d]) -> Generator[c|d,None,None]:
    yield from iter1
    yield from iter2

class DictComparerSection(ComparerSection.ComparerSection[dict[c, d]]):

    def __init__(
            self,
            name:str,
            comparer:ComparerSection.ComparerSection[d]|None|dict[type,ComparerSection.ComparerSection[d]|None],
            types:tuple[type,...]|None,
            detect_key_moves:bool=False,
            comparison_move_function:Callable[[c, d], b]|None=None,
            measure_length:bool=False,
            print_all:bool=False,
            normalizer:Normalizer.Normalizer|None=None,
            children_has_normalizer:bool=False,
        ) -> None:
        ''' * `name` is what the key of this dictionary is.
         * If `comparer` is a ComparerSection, then it will compare and print all values using that ComparerSection.
         * If `comparer` is None, then it will use `stringify` in place of a printer and not compare.
         * If `comparer` is a list of tuples of Callables and ComparerSections, then each key and value will be fed into the Callables until one returns True, and the corresponding ComparerSection will be used for that one.
         * If `comparer` is a list of tuples of strs and ComparerSections, then each key will be searched in the list, and the corresponding ComparerSection will be used.
         * If `comparer` is a list and a match cannot be found, then a KeyError is raised.
         * `comparer` can contain both strs and Callables when a list.
         * If `key_types` or `value_types` is an Iterable of types, then it will check if the key/value is an instance of at least one type in the list (if not, raise TypeError).
         * If `key_types` or `value_types` is a Callable, then it will call the Callable with the key and value. If the Callable returns False, then it will raise a TypeError.
         * If `key_types` or `value_types` is None, then the type of the key/value will not be checked.
         * `key_types`, `value_types`, and `comparer` are never given a D.Diff; Diffs are split into old and new and compared separately.
         * `detect_key_moves` controls whether it will look for changes in keys.
         * `comparison_move_function` is called with a key and value, and returns a piece of the value. It is used to compare the change in keys between two data.
         * If `comparison_move_function` returns None, then it will not attempt to detect moves for that value.
         * If `measure_length` is True, then it will show how the length of the data changed when comparing.
         * If `print_all` is True, then if there is a change in one part of the data, then all parts will be printed.'''

        self.name = name
        self.comparer = comparer
        self.types = (object,) if types is None else types
        self.detect_key_moves = detect_key_moves
        self.comparison_move_function = (lambda key, value: value) if comparison_move_function is None else comparison_move_function
        self.measure_length = measure_length
        self.print_all = print_all
        self.normalizer = normalizer
        self.children_has_normalizer = children_has_normalizer
        self.check_initialization_parameters()

    def check_initialization_parameters(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("`name` is not a str!")
        if not (self.comparer is None or isinstance(self.comparer, (ComparerSection.ComparerSection, dict))):
            raise TypeError("`comparer` is not a ComparerSection, NoneType, or list!")
        if isinstance(self.comparer, dict):
            for comparer_index, (comparer_key, comparer_value) in enumerate(self.comparer.items()):
                if not isinstance(comparer_key, type):
                    raise TypeError("Key number %i of `comparer` is not a type!" % (comparer_index))
                if not (comparer_value is None or isinstance(comparer_value, ComparerSection.ComparerSection)):
                    raise TypeError("Key \"%s\" of `comparer` is not a ComparerSection or None!" % (comparer_key.__name__))
        if not isinstance(self.types, tuple) and self.types is not None:
            raise TypeError("`value_types` is not a tuple or None!")
        if isinstance(self.types, tuple) and not all(isinstance(item, (type)) for item in self.types):
            raise TypeError("An item of `value_types` is not a type!")
        if not isinstance(self.detect_key_moves, bool):
            raise TypeError("`detect_key_moves` is not a bool!")
        if not isinstance(self.comparison_move_function, Callable) and self.comparison_move_function is not None:
            raise TypeError("`comparison_move_function` is not a Callable or None!")
        if not isinstance(self.measure_length, bool):
            raise TypeError("`measure_length` is not a bool!")
        if not isinstance(self.print_all, bool):
            raise TypeError("`print_all` is not a bool!")
        if not (self.normalizer is None or isinstance(self.normalizer, Normalizer.Normalizer)):
            raise TypeError("`normalizer` is not a Normalizer or None!")
        if not isinstance(self.children_has_normalizer, bool):
            raise TypeError("`children_has_normalizer` is not a bool!")

    def check_type(self, key:c, value:d, trace:Trace.Trace) -> tuple[Trace.Trace,Exception]|None:
        if isinstance(key, D.Diff) or isinstance(value, D.Diff):
            raise TypeError("`check_type` was given data containing Diffs!")
        if not isinstance(value, self.types):
            return (trace.copy(self.name, key), TypeError("Key, value %s: %s in %s excepted because value is not %s!" % (CU.stringify(key), CU.stringify(value), self.name, self.types)))

    def check_all_types(self, data:dict[c,d], trace:Trace.Trace, normalizer_dependencies:Normalizer.LocalNormalizerDependencies) -> list[tuple[Trace.Trace,Exception]]:
        '''Recursively checks if the types are correct. Should not be given data containing Diffs.'''
        output:list[tuple[Trace.Trace,Exception]] = []
        if not isinstance(data, dict):
            output.append((trace, TypeError("`data` has the wrong type, %s instead of dict!" % type(data))))
            return output
        for key, value in data.items():
            check_type_output = self.check_type(key, value, trace)
            if check_type_output is not None:
                assert check_type_output[0] is not None
                output.append(check_type_output)
                continue

            comparer_set = self.choose_comparer(key, value, trace)
            if len(comparer_set) != 1 or D.DiffType.not_diff not in comparer_set:
                raise TypeError("`check_all_types` was given data containing Diffs!")
            comparer = comparer_set[D.DiffType.not_diff]
            if comparer is not None:
                output.extend(comparer.check_all_types(value, trace.copy(self.name, key), normalizer_dependencies))
        return output

    def normalize(self, data:dict[c,d], normalizer_dependencies:Normalizer.LocalNormalizerDependencies, version_number:int, trace:Trace.Trace) -> None:
        if not self.children_has_normalizer: return
        if self.normalizer is not None:
            self.normalizer(data, normalizer_dependencies, version_number)
        for key, value in data.items():
            try:
                comparer_set = self.choose_comparer(key, value, trace)
            except Exception:
                # it hasn't been type checked yet, so something could except
                continue
            if len(comparer_set) != 1 or D.DiffType.not_diff not in comparer_set:
                raise TypeError("`normalize` was given data containing Diffs in %s in %s: %s. comparer set is %s; excepted on key: value %s: %s" % (self.name, trace, data, comparer_set, key, value))
            comparer = comparer_set[D.DiffType.not_diff]
            if comparer is not None:
                comparer.normalize(value, normalizer_dependencies, version_number, trace.copy(self.name, key))

    def compare(
            self,
            data1:dict[c,d],
            data2:dict[c,d],
            trace:Trace.Trace,
            normalizer_dependencies:Normalizer.LocalNormalizerDependencies
        ) -> tuple[dict[c|D.Diff[c,c],d|D.Diff[d,d]],list[tuple[Trace.Trace,Exception]]]:
        key_occurences:dict[c,list[D.DiffType]] = {}
        exceptions:list[tuple[Trace.Trace,Exception]] = []

        # get occurence counts
        data1_iterator = zip(infinite_generator(D.DiffType.old), data1.items()) # since zip stops at the shortest iterator, this will not run forever.
        data2_iterator = zip(infinite_generator(D.DiffType.new), data2.items())
        for diff_type, (key, value) in glue_iterables(data1_iterator, data2_iterator):
            if (check_type_exception := self.check_type(key, value, trace)) is not None:
                exceptions.append(check_type_exception)
            if key in key_occurences:
                key_occurences[key].append(diff_type)
            else:
                key_occurences[key] = [diff_type]

        data_for_add_remove_change_compare:dict[c|D.Diff[c,c],tuple[tuple[D.DiffType, d],...]] = {}
        # assemble key change dicts.
        if self.detect_key_moves:
            old_comparison_values:list[tuple[c,b]] = []
            new_comparison_values:list[tuple[c,b]] = []
        for key, occurences in key_occurences.items():
            if len(occurences) == 1:
                match self.detect_key_moves, occurences[0]:
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
            elif len(occurences) == 2:
                data_for_add_remove_change_compare[key] = ((D.DiffType.old, data1[key]), (D.DiffType.new, data2[key]))
            else:
                raise RuntimeError("Illegal state!")

        if self.detect_key_moves: # if False, then additions and removals are added to data_for_add_remove_change_compare above.
            # find matching values.
            new_keys_involved_in_key_change:set[c] = set()
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

        output:dict[c|D.Diff[c,c],d|D.Diff[d,d]] = {}
        for key, occurences in data_for_add_remove_change_compare.items():
            if len(occurences) == 2:
                value1, value2 = occurences[0][1], occurences[1][1]
                if value1 == value2:
                    # no change occurred, so nothing needs to be done whatsoever on this data. If the previous, identical data was
                    # verified, then this would be correct data too.
                    output[key] = value1
                else:
                    comparer_set = self.choose_comparer(key, D.Diff(value1, value2), trace)
                    output[key], new_exceptions = comparer_set.compare(value1, value2, trace.copy(self.name, key), normalizer_dependencies)
                    exceptions.extend(new_exceptions)
                    continue
            elif len(occurences) == 1:
                # since there's now only one value, there's no more comparing to do.
                # key can only be a D.Diff when len(occurences) == 2
                if occurences[0][0] == D.DiffType.old: diff_key, diff_value = D.Diff(old=key), D.Diff(old=occurences[0][1])
                elif occurences[0][0] == D.DiffType.new: diff_key, diff_value = D.Diff(new=key), D.Diff(new=occurences[0][1])
                else: raise RuntimeError("Illegal state!")
                output[diff_key] = diff_value
                continue
            else:
                raise RuntimeError("Illegal state: %s, %s" % (key, occurences))

        return {key: value for key, value in sorted(output.items())}, exceptions

    def choose_comparer(self, key:c, value:d, trace:Trace.Trace) -> ComparerSet.ComparerSet:
        output:dict[D.DiffType,ComparerSection.ComparerSection] = {}
        for value_iter, value_diff_type in D.iter_diff(value):
            if isinstance(self.comparer, dict):
                output[value_diff_type] = self.comparer[type(value_iter)]
                # errors should be caught by the type checker.
            else:
                output[value_diff_type] = self.comparer
        return ComparerSet.ComparerSet(output)

    def print_item(self, key:c, value:d, comparer_set:ComparerSet.ComparerSet[d], trace:Trace.Trace, message:str="") -> list[str]:
        subcomparer_output = comparer_set.print_text(D.DiffType.not_diff, value, trace.copy(self.name, key))
        match len(subcomparer_output):
            case 0:
                return ["%s%s %s: empty" % (message, self.name, CU.stringify(key))]
            case 1:
                return ["%s%s %s: %s" % (message, self.name, CU.stringify(key), subcomparer_output[0])]
            case _:
                output:list[str] = []
                output.append("%s%s %s:" % (message, self.name, CU.stringify(key)))
                output.extend("\t" + line for line in subcomparer_output)
                return output

    def print_text(self, data:dict[c, d], trace:Trace.Trace) -> list[str]:
        output:list[str] = []
        if not isinstance(data, dict):
            raise TypeError("`data` is not a dict at %s, but instead type %s!" % (trace.give_key(self.name), type(data)))
        for key, value in data.items():
            comparer_set = self.choose_comparer(key, value, trace)
            output.extend(self.print_item(key, value, comparer_set, trace))
        return output

    def compare_text(self, data:dict[c, d], trace:Trace.Trace) -> tuple[list[str],bool]:
        output:list[str] = []
        any_changes = False
        if not isinstance(data, dict):
            raise TypeError("`data` is not a dict at %s, but instead type %s!" % (trace.give_key(self.name), type(data)))
        current_length, addition_length, removal_length = 0, 0, 0
        size_changed = False
        for key, value in data.items():
            can_print_print_all = True # if the print_all thing is overridden for whatever reason.
            key_str = key.first_existing_property() if isinstance(key, D.Diff) else key
            comparer_set = self.choose_comparer(key, value, trace)

            if isinstance(key, D.Diff) and key.is_change:
                can_print_print_all = False
                any_changes = True
                output.append("Moved %s %s to %s." % (self.name, CU.stringify(key.old), CU.stringify(key.new)))
            if isinstance(value, D.Diff):
                any_changes = True
                size_changed = True
                match value.change_type:
                    case D.ChangeType.addition:
                        current_length += 1; addition_length += 1
                        self.print_single(key_str, value.new, "Added", output, comparer_set[D.DiffType.new], trace)
                    case D.ChangeType.change:
                        current_length += 1
                        self.print_double(key_str, value.old, value.new, "Changed", output, comparer_set, trace)
                    case D.ChangeType.removal:
                        removal_length += 1
                        self.print_single(key_str, value.old, "Removed", output, comparer_set[D.DiffType.old], trace)
            else:
                current_length += 1
                if comparer_set[D.DiffType.not_diff] is None:
                    if self.print_all and can_print_print_all:
                        output.extend(self.print_item(key_str, value, comparer_set, trace, message="Unchanged "))
                    pass # This means that it is not a difference and does not contain differences.
                else:
                    subcomparer_lines, has_changes = comparer_set.compare_text(D.DiffType.not_diff, value, trace.copy(self.name, key_str))
                    if has_changes:
                        any_changes = True
                        output.append("Changed %s %s:" % (self.name, CU.stringify(key_str)))
                        output.extend("\t" + line for line in subcomparer_lines)
                    elif self.print_all and can_print_print_all:
                        output.extend(self.print_item(key_str, value, comparer_set, trace, message="Unchanged "))
        if self.measure_length and size_changed:
            output = ["Total %s: %i (+%i, -%i)" % (self.name, current_length, addition_length, removal_length)] + output
        return output, any_changes
