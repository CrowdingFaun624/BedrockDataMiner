import json
import traceback
from typing import Any, Callable, Generator, Generic, Iterable, TypeVar, TYPE_CHECKING, Union
from types import UnionType

import Comparison.Difference as D
import Utilities.FileManager as FileManager
import Utilities.VersionTags as VersionTags

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

a = TypeVar("a")
b = TypeVar("b")
c = TypeVar("c", object, D.Diff)
d = TypeVar("d", object, D.Diff)

file_counts:dict[str,int] = {}

def infinite_generator(item:a) -> Generator[a,None,None]:
    '''A generator that returns the same value forever.'''
    while True:
        yield item
def glue_iterables(iter1:Iterable[a], iter2:Iterable[b]) -> Generator[a|b,None,None]:
    yield from iter1
    yield from iter2

def stringify(data:Any) -> str:
    '''Returns the string of data containing no Diffs. Is used in the comparison reporter.'''
    return json.dumps(data)

class Trace():
    def __init__(self, data:list[tuple[str,str|int]]=None, current_key:str=None) -> None:
        self.data = [] if data is None else data
        self.current_key = current_key

    def copy(self, name:str|None=None, key:str|int|None=None) -> "Trace":
        if name is None:
            return Trace(self.data.copy())
        else:
            new_trace = self.data.copy()
            new_trace.append((name, key))
            return Trace(new_trace)

    def give_key(self, current_key:str|int) -> "Trace":
        self.current_key = current_key

    def __str__(self) -> str:
        if self.current_key is None:
            return ".".join("%s[%s]" % (name, index) for name, index in self.data)
        else:
            if len(self.data) == 0:
                return self.current_key
            else:
                return ".".join("%s[%s]" % (name, index) for name, index in self.data) + ".%s" % (self.current_key)

class ComparerSection(Generic[a]):
    def __init__(self, name:str) -> None:
        self.name = name
        self.check_initialization_parameters()
    
    def check_initialization_parameters(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("`name` is not a str!")

    def __repr__(self) -> str:
        return "<ComparerSection %s>" % self.name

    def print_single(self, key_str:str|None, data:d, message:str, output:list[str], printer:Union["ComparerSection[d]",None], trace:Trace) -> None:
        if printer is None:
            stringified_data = stringify(data)
            if key_str is None:
                output.append("%s %s %s." % (message, self.name, stringified_data))
            else:
                output.append("%s %s %s of %s." % (message, self.name, stringify(key_str), stringified_data))
        else:
            new_trace = trace.copy(self.name, key_str)
            subcomparer_output = self.check_printer_output(printer.print_text(data, new_trace), new_trace)
            if len(subcomparer_output) == 0:
                if key_str is None:
                    output.append("%s empty %s." % (message, self.name))
                else:
                    output.append("%s empty %s %s." % (message, self.name, stringify(key_str)))
            elif len(subcomparer_output) == 1:
                if key_str is None:
                    output.append("%s %s %s." % (message, self.name, subcomparer_output[0]))
                else:
                    output.append("%s %s %s of %s." % (message, self.name, stringify(key_str), subcomparer_output[0]))
            else:
                if key_str is None:
                    output.append("%s %s:" % (message, self.name))
                else:
                    output.append("%s %s %s:" % (message, self.name, stringify(key_str)))
                output.extend("\t" + line for line in subcomparer_output)

    def print_double(self, key_str:str|None, data1:d, data2:d, message:str, output:list[str], printers:"ComparerSet", trace:Trace) -> None:
        new_trace = trace.copy(self.name, key_str)
        subcomparer_output1 = self.check_printer_output(printers.print_text(0, data1, new_trace), new_trace)
        subcomparer_output2 = self.check_printer_output(printers.print_text(-1, data2, new_trace), new_trace) # [-1] because it must be the last item anyways.
        if len(subcomparer_output1) == 0: subcomparer_output1 = ["empty"]
        if len(subcomparer_output2) == 0: subcomparer_output2 = ["empty"]
        if len(subcomparer_output1) == 1 and len(subcomparer_output2) == 1:
            if key_str is None:
                output.append("%s %s from %s to %s." % (message, self.name, subcomparer_output1[0], subcomparer_output2[0]))
            else:
                output.append("%s %s %s from %s to %s." % (message, self.name, stringify(key_str), subcomparer_output1[0], subcomparer_output2[0]))
        elif len(subcomparer_output1) == 1 and len(subcomparer_output2) > 1:
            if key_str is None:
                output.append("%s %s from %s to:" % (message, self.name, subcomparer_output1[0]))
            else:
                output.append("%s %s %s from %s to:" % (message, self.name, stringify(key_str), subcomparer_output1[0]))
            output.extend("\t" + line for line in subcomparer_output2)
        elif len(subcomparer_output1) > 1 and len(subcomparer_output2) == 1:
            if key_str is None:
                output.append("%s %s to %s from:" % (message, self.name, subcomparer_output2[0]))
            else:
                output.append("%s %s %s to %s from:" % (message, self.name, stringify(key_str), subcomparer_output2[0]))
            output.extend("\t" + line for line in subcomparer_output1)
        else:
            if key_str is None:
                output.append("%s %s from:" % (message, self.name))
            else:
                output.append("%s %s %s from:" % (message, self.name, stringify(key_str)))
            output.extend("\t" + line for line in subcomparer_output1)
            output.append("to:")
            output.extend("\t" + line for line in subcomparer_output2)

    def check_comparer_output(self, output:a, trace:Trace) -> a:
        if not isinstance(output, tuple):
            raise TypeError("%s did not return a tuple!" % (trace.give_key(self.name)))
        if len(output) != 2:
            raise ValueError("%s did not return a tuple with length 2!" % (trace.give_key(self.name)))
        if not isinstance(output[0], list):
            raise TypeError("The first item of the return of %s is not a list!" % (trace.give_key(self.name)))
        if not isinstance(output[1], bool):
            raise TypeError("The second item of the return of %s is not a bool!" % (trace.give_key(self.name)))
        if output[1] is True and len(output[0]) == 0:
            raise ValueError("The first item of the return of %s is empty and should not be!" % (trace.give_key(self.name)))
        if not all(isinstance(line, str) for line in output[0]):
            raise TypeError("An item of the first item of the return of %s is not a str!" % (trace.give_key(self.name)))
        return output

    def check_printer_output(self, output:a, trace:Trace) -> a:
        if not isinstance(output, list):
            raise TypeError("%s did not return a list!" % (trace.give_key(self.name)))
        if not all(isinstance(line, str) for line in output):
            raise TypeError("An item of the return value of %s is not a str!" % (trace.give_key(self.name)))
        return output

    def check_types(self, data:a, trace:Trace) -> list[tuple[Trace, Exception]]: ...
    def compare_text(self, data:a, trace:Trace) -> tuple[list[str],bool]: ...
    def print_text(self, data:a, trace:Trace) -> list[str]: ...
    def compare(self, data1:a, data2:a, trace:Trace) -> a: ...

class ComparerSet(Generic[d]):
    '''Contains one or two ComparerSections. Is used internally.
    Is used for when a value is a Diff and must use two different printers.'''
    def __init__(self, comparers:dict[D.DiffType,ComparerSection]) -> None:
        if not isinstance(comparers, dict):
            raise TypeError("`comparers` is not a dict!")
        if len(comparers) == 0:
            raise ValueError("`comparers is length 0!")
        if len(comparers) > 2:
            raise ValueError("`comparers` is greater than length 2 (length %i)!" % len(comparers))
        if not all(isinstance(key, D.DiffType) for key in comparers.keys()):
            raise TypeError("A key of `comparers` is not a DiffType!")
        if not all(isinstance(value, ComparerSection) or value is None for value in comparers.values()):
            raise TypeError("A value of `comparers` is not a ComparerSection or None!")

        self.comparers = comparers

    def __repr__(self) -> str:
        return "<ComparerSet %s>" % self.comparers

    def __len__(self) -> int:
        return len(self.comparers)
    def __contains__(self, item:D.DiffType) -> bool:
        return item in self.comparers
    def __getitem__(self, key:D.DiffType|int) -> ComparerSection|None:
        if isinstance(key, D.DiffType):
            return self.comparers[key]
        elif isinstance(key, int):
            return list(self.comparers.values())[key]
        else:
            raise KeyError("Attempted to index a ComparerSet using a %s rather than a D.DiffType!" % type(key))
    def print_text(self, key:D.DiffType|int, data:d, trace:Trace) -> list[str]:
        comparer = self[key]
        if comparer is None:
            return [stringify(data)]
        else:
            return comparer.print_text(data, trace)
    def compare_text(self, key:D.DiffType|int, data:d, trace:Trace) -> tuple[list[str],bool]:
        comparer = self[key]
        if comparer is None:
            raise RuntimeError("Attempted to compare (key %s) using a NoneType object at %s!" % (key, trace))
        else:
            return comparer.compare_text(data, trace)
    def compare(self, data1:d, data2:d, trace:Trace) -> d:
        if (len(self) == 1) or (len(self) == 2 and self[0] == self[1]):
            # both items have the same ComparerSection.
            comparer = self[0]
            if comparer is None:
                return D.Diff(data1, data2)
            else:
                # items must be not equal because then the D.Diff could not be created.
                return comparer.compare(data1, data2, trace)
        else:
            # items have different data types.
            return D.Diff(data1, data2)

class DictComparerSection(ComparerSection[dict[c, d]]):
    def __init__(
            self,
            name:str,
            comparer:ComparerSection[d]|None|dict[type,ComparerSection[d]|None],
            types:tuple[type]|None,
            detect_key_moves:bool=False,
            comparison_move_function:Callable[[c, d], b]|None=None,
            measure_length:bool=False,
            print_all:bool=False,
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
        self.check_initialization_parameters()

    def check_initialization_parameters(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("`name` is not a str!")
        if not (self.comparer is None or isinstance(self.comparer, (ComparerSection, dict))):
            raise TypeError("`comparer` is not a ComparerSection, NoneType, or list!")
        if isinstance(self.comparer, dict):
            for comparer_index, (comparer_key, comparer_value) in enumerate(self.comparer.items()):
                if not isinstance(comparer_key, type):
                    raise TypeError("Key number %i of `comparer` is not a type!" % (comparer_index))
                if not (comparer_value is None or isinstance(comparer_value, ComparerSection)):
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

    def check_types(self, data:dict[c,d], trace:Trace) -> list[tuple[Trace,Exception]]:
        '''Recursively checks if the types are correct. Should not be given data containing Diffs.'''
        output:list[tuple[Trace,Exception]] = []
        if not isinstance(data, dict):
            output.append((trace, TypeError("`data` has the wrong type, %s instead of dict!" % type(data))))
            return output
        for key, value in data.items():
            new_trace = trace.copy(self.name, key)
            if isinstance(key, D.Diff) or isinstance(value, D.Diff):
                raise TypeError("`check_types` was given data containg Diffs!")

            if not isinstance(value, self.types):
                output.append((new_trace.copy().give_key(self.name), TypeError("Key, value %s: %s in %s excepted because value is not %s!" % (stringify(key), stringify(value), self.name, self.types))))
                continue

            comparer_set = self.choose_comparer(key, value)
            if len(comparer_set) != 1 or D.DiffType.not_diff not in comparer_set:
                raise TypeError("`check_types` was given data containg Diffs!")
            comparer = comparer_set[D.DiffType.not_diff]
            if comparer is not None:
                output.extend(comparer.check_types(value, new_trace))
        return output

    def compare(self, data1: dict[c,d], data2: dict[c,d], trace:Trace) -> dict[c|D.Diff[c,c],d|D.Diff[d,d]]:
        key_occurences:dict[c,list[D.DiffType]] = {}

        # get occurence counts
        data1_iterator = zip(infinite_generator(D.DiffType.old), data1.items()) # since zip stops at the shortest iterator, this will not run forever.
        data2_iterator = zip(infinite_generator(D.DiffType.new), data2.items())
        for diff_type, (key, value) in glue_iterables(data1_iterator, data2_iterator):
            if key in key_occurences:
                key_occurences[key].append(diff_type)
            else:
                key_occurences[key] = [diff_type]

        data_for_add_remove_change_compare:dict[c|D.Diff[c,c],tuple[tuple[D.DiffType, d],...]] = {}
        # assemble key change dicts.
        if self.detect_key_moves:
            old_comparison_values:list[tuple[c,a]] = []
            new_comparison_values:list[tuple[c,a]] = []
        for key, occurences in key_occurences.items():
            if len(occurences) == 1:
                if self.detect_key_moves and occurences[0] == D.DiffType.old: # will test for key change and is only in old
                    comparison_move_function_return = self.comparison_move_function(key, data1[key])
                    # If `comparison_move_function_return` is None, do not detect key change.
                    if comparison_move_function_return is None: data_for_add_remove_change_compare[key] = ((D.DiffType.old, data1[key]),)
                    else: old_comparison_values.append((key, comparison_move_function_return))
                elif self.detect_key_moves and occurences[0] == D.DiffType.new: # will not test for key change and is only in old
                    comparison_move_function_return = self.comparison_move_function(key, data2[key])
                    if comparison_move_function_return is None: data_for_add_remove_change_compare[key] = ((D.DiffType.new, data2[key]),)
                    else: new_comparison_values.append((key, comparison_move_function_return))
                elif not self.detect_key_moves and occurences[0] == D.DiffType.old: # will test for key change and is only in new
                    data_for_add_remove_change_compare[key] = ((D.DiffType.old, data1[key]),)
                elif not self.detect_key_moves and occurences[0] == D.DiffType.new: # will not test for key change and is only in new
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
                    output[key] = value1
                else:
                    comparer_set = self.choose_comparer(key, D.Diff(value1, value2))
                    output[key] = comparer_set.compare(value1, value2, trace.copy(self.name, key))
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
                print(key, occurences)
                raise RuntimeError("Illegal state!")
        return {key: value for key, value in sorted(output.items())}

    def choose_comparer(self, key:c, value:d) -> ComparerSet:
        output:dict[D.DiffType,ComparerSection] = {}
        for key_iter, value_iter, key_diff_type, value_diff_type in D.double_iter_diff(key, value):
            if isinstance(self.comparer, dict):
                output[value_diff_type] = self.comparer[type(value_iter)]
                # errors should be caught by the type checker.
            else:
                output[value_diff_type] = self.comparer
        return ComparerSet(output)

    def print_item(self, key:c, value:d, comparer_set:ComparerSet[d], trace:Trace, message:str="") -> list[str]:
        new_trace = trace.copy(self.name, key)
        subcomparer_output = self.check_printer_output(comparer_set.print_text(D.DiffType.not_diff, value, new_trace), new_trace)
        if len(subcomparer_output) == 0:
            return ["%s%s %s: empty" % (message, self.name, stringify(key))]
        elif len(subcomparer_output) == 1:
            return ["%s%s %s: %s" % (message, self.name, stringify(key), subcomparer_output[0])]
        else:
            output:list[str] = []
            output.append("%s%s %s:" % (message, self.name, stringify(key)))
            output.extend("\t" + line for line in subcomparer_output)
            return output

    def print_text(self, data:dict[c, d], trace:Trace) -> list[str]:
        output:list[str] = []
        if not isinstance(data, dict):
            raise TypeError("`data` is not a dict at %s, but instead type %s!" % (trace.give_key(self.name), type(data)))
        for key, value in data.items():
            comparer_set = self.choose_comparer(key, value)
            output.extend(self.print_item(key, value, comparer_set, trace))
        return output

    def compare_text(self, data:dict[c, d], trace:Trace) -> tuple[list[str],bool]:
        output:list[str] = []
        any_changes = False
        if not isinstance(data, dict):
            raise TypeError("`data` is not a dict at %s, but instead type %s!" % (trace.give_key(self.name), type(data)))
        current_length, addition_length, removal_length = 0, 0, 0
        size_changed = False
        for key, value in data.items():
            can_print_print_all = True # if the print_all thing is overridden for whatever reason.
            key_str = key.first_existing_property() if isinstance(key, D.Diff) else key
            comparer_set = self.choose_comparer(key, value)

            if isinstance(key, D.Diff):
                if key.is_addition:
                    pass # Behavior is handled in the check for `value` being a `D.Diff`.
                elif key.is_change:
                    can_print_print_all = False
                    any_changes = True
                    output.append("Moved %s %s to %s." % (self.name, stringify(key.old), stringify(key.new)))
                elif key.is_removal:
                    pass # Behavior is handled in the check for `value` being a `D.Diff`.
            else:
                pass
            if isinstance(value, D.Diff):
                any_changes = True
                size_changed = True
                if value.is_addition:
                    current_length += 1; addition_length += 1
                    self.print_single(key_str, value.new, "Added", output, comparer_set[D.DiffType.new], trace)
                elif value.is_change:
                    current_length += 1
                    self.print_double(key_str, value.old, value.new, "Changed", output, comparer_set, trace)
                elif value.is_removal:
                    removal_length += 1
                    self.print_single(key_str, value.old, "Removed", output, comparer_set[D.DiffType.old], trace)
            else:
                current_length += 1
                if comparer_set[D.DiffType.not_diff] is None:
                    if self.print_all and can_print_print_all:
                        output.extend(self.print_item(key_str, value, comparer_set, trace, message="Unchanged "))
                    pass # This means that it is not a difference and does not contain differences.
                else:
                    new_trace = trace.copy(self.name, key_str)
                    subcomparer_lines, has_changes = self.check_comparer_output(comparer_set.compare_text(D.DiffType.not_diff, value, new_trace), new_trace)
                    if has_changes:
                        any_changes = True
                        output.append("Changed %s %s:" % (self.name, stringify(key_str)))
                        output.extend("\t" + line for line in subcomparer_lines)
                    elif self.print_all and can_print_print_all:
                        output.extend(self.print_item(key_str, value, comparer_set, trace, message="Unchanged "))
        if self.measure_length and size_changed:
            output = ["Total %s: %i (+%i, -%i)" % (self.name, current_length, addition_length, removal_length)] + output
        return output, any_changes

class ListComparerSection(ComparerSection[Iterable[d]]):
    def __init__(
            self,
            name:str,
            comparer:ComparerSection[d]|None|dict[type,ComparerSection[d]|None],
            types:tuple[type]|None,
            print_flat:bool=False,
            ordered:bool=True,
            measure_length:bool=False,
            print_all:bool=False
        ) -> None:
        ''' * `name` is what the key of this dictionary is.
         * If `comparer` is a ComparerSection, then it will compare and print all items using that ComparerSection.
         * If `comparer` is None, then it will use `stringify` in place of a printer and not compare.
         * If `comparer` is a list of tuples of Callables and ComparerSections, then each index and item will be fed into the Callables until one returns True, and the corresponding ComparerSection will be used for that one.
         * If `comparer` is a list and a match cannot be found, then a KeyError is raised.
         * If `types` is an Iterable of types, then it will check if the item is an instance of at least one type in the list (if not, raise TypeError).
         * If `types` is a Callable, then it will call the Callable with the index and item. If the Callable returns False, then it will raise a TypeError.
         * If `types` is None, then the type of the key/value will not be checked.
         * `types` is never given a D.Diff; Diffs are split into old and new and compared separately.
         * If `print_flat` is True, then lists are printed such as [item1, item2, item3].
         * If `print_flat` is False: then lists are printed such as 0: item1\\n1: item2\\n2: item3
         * If `measure_length` is True, then it will show how the length of the data changed when comparing.
         * If `print_all` is True, then if there is a change in one part of the data, then all parts will be printed.'''

        self.name = name
        self.comparer = comparer
        self.types = [object] if types is None else types
        self.print_flat = print_flat
        self.ordered = ordered
        self.measure_length = measure_length
        self.print_all = print_all
        self.check_initialization_parameters()

    def check_initialization_parameters(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("`name` is not a str!")
        if not (self.comparer is None or isinstance(self.comparer, (ComparerSection, dict))):
            raise TypeError("`comparer` is not a ComparerSection, dict, or None!")
        if isinstance(self.comparer, dict):
            for comparer_index, (comparer_key, comparer_value) in enumerate(self.comparer.items()):
                if not isinstance(comparer_key, type):
                    raise TypeError("Key number %i of `comparer` is not a type!" % (comparer_index))
                if not (comparer_value is None or isinstance(comparer_value, ComparerSection)):
                    raise TypeError("Key \"%s\" of `comparer` is not a ComparerSection or None!" % (comparer_key.__name__))
        if not (self.types is None or isinstance(self.types, tuple)):
            raise TypeError("`types` is not an a tuple or None but instead a \"%s\"!" % self.types.__class__.__name__)
        if isinstance(self.types, tuple) and not all(isinstance(item, (type, UnionType)) for item in self.types):
            raise TypeError("An item of `types` is not a type!")
        if not isinstance(self.print_flat, bool):
            raise TypeError("`print_flat` is not a bool!")
        if not isinstance(self.measure_length, bool):
            raise TypeError("`measure_length` is not a bool!")
        if not isinstance(self.print_all, bool):
            raise TypeError("`print_all` is not a bool!")

    def check_types(self, data:list[d], trace:Trace) -> list[tuple[list[tuple[str,str]],Exception]]:
        '''Recursively checks if the types are correct. Should not be given data containing Diffs.'''
        output:list[list[tuple[int,d]]] = []
        for index, item in enumerate(data):
            new_trace = trace.copy(self.name, index)
            if isinstance(item, D.Diff):
                raise TypeError("`check_types` was given data containg Diffs!")

            if not isinstance(item, self.types):
                output.append((new_trace.copy().give_key(self.name), TypeError("Index, item %i: %s in %s excepted because item is not %s!" % (index, stringify(item), self.name, self.types))))
                continue

            comparer_set = self.choose_comparer(index, item)
            if len(comparer_set) != 1 or D.DiffType.not_diff not in comparer_set:
                raise TypeError("`check_types` was given data containg Diffs!")
            comparer = comparer_set[D.DiffType.not_diff]
            if comparer is not None:
                output.extend(comparer.check_types(item, new_trace))
        return output

    def compare(self, data1:Iterable[d], data2:Iterable[d], trace:Trace) -> Iterable[d]:
        output:list[d|D.Diff[d]] = []
        if self.ordered:
            index = -1
            for index, (item1, item2) in enumerate(zip(data1, data2)):
                if item1 == item2:
                    output.append(item1)
                else:
                    comparer_set = self.choose_comparer(index, D.Diff(item1, item2))
                    output.append(comparer_set.compare(item1, item2, trace.copy(self.name, index)))
            # now, only the shortest iterable has been consumed.
            if len(data1) > len(data2):
                output.extend(D.Diff(old=data1[i]) for i in range(index + 1, len(data1)))
            elif len(data2) > len(data1):
                output.extend(D.Diff(new=data2[i]) for i in range(index + 1, len(data2)))
            else: pass
            return output
        else: # unordered can only have additions or removals, no changes.
            for item in data1:
                if item in data2:
                    output.append(item) # item in both
                else:
                    output.append(D.Diff(old=item))
            for item in data2:
                if item in data1:
                    pass # ignore; already added.
                else:
                    output.append(D.Diff(new=item))
            return output

    def choose_comparer(self, index:int, item:d) -> ComparerSet:
        output:dict[D.DiffType,ComparerSection] = {}
        for item_iter, diff_type in D.iter_diff(item):
            if isinstance(self.comparer, dict):
                output[diff_type] = self.comparer[type(item_iter)]
            else:
                output[diff_type] = self.comparer
        return ComparerSet(output)

    def print_item(self, index:int, item:d, subcomparer_output:list[str], message:str="") -> list[str]:
        if len(subcomparer_output) == 0:
            if self.ordered:
                return ["%s%s %i: empty" % (message, self.name, index)]
            else:
                return ["%s%s: empty" % (message, self.name)]
        elif len(subcomparer_output) == 1:
            if self.ordered:
                return ["%s%s %i: %s" % (message, self.name, index, subcomparer_output[0])]
            else:
                return ["%s%s: %s" % (message, self.name, subcomparer_output[0])]
        else:
            output:list[str] = []
            if self.ordered:
                output.append("%s%s %i:" % (message, self.name, index))
            else:
                output.append("%s%s:" % (message, self.name))
            output.extend("\t" + line for line in subcomparer_output)
            return output

    def print_text(self, data:Iterable[d], trace:Trace) -> list[str]:
        output:list[str] = []
        items_str:list[str] = [] # print_flat only
        if not isinstance(data, Iterable):
            raise TypeError("`data` is not an Iterable at %s, but instead type %s!" % (trace.give_key(self.name), type(data)))
        for index, item in enumerate(data):
            comparer_set = self.choose_comparer(index, item)

            new_trace = trace.copy(self.name, index)
            subcomparer_output = self.check_printer_output(comparer_set.print_text(D.DiffType.not_diff, item, new_trace), new_trace)
            if self.print_flat:
                if len(subcomparer_output) == 1:
                    items_str.append(subcomparer_output[0])
                else:
                    raise RuntimeError("Subcomparer of flat-printing %s returned multiple lines!" % (trace.give_key(self.name)))
            else:
                output.extend(self.print_item(index, item, subcomparer_output))
        if self.print_flat:
            output.append("[" + ", ".join(items_str) + "]")
        return output

    def compare_text(self, data:Iterable[d], trace:Trace) -> tuple[list[str],bool]:
        output:list[str] = []
        any_changes = False
        if not isinstance(data, Iterable):
            raise TypeError("`data` is not an Iterable at %s, but instead type %s!" % (trace, type(data)))
        current_length, addition_length, removal_length = 0, 0, 0
        size_changed = False
        for index, item in enumerate(data):
            comparer_set = self.choose_comparer(index, item)

            if isinstance(item, D.Diff):
                any_changes = True
                print_key_str = index if self.ordered else None
                size_changed = True
                if item.is_addition:
                    current_length += 1; addition_length += 1
                    self.print_single(print_key_str, item.new, "Added", output, comparer_set[D.DiffType.new], trace)
                elif item.is_change:
                    current_length += 1
                    self.print_double(print_key_str, item.old, item.new, "Changed", output, comparer_set, trace)
                elif item.is_removal:
                    removal_length += 1
                    self.print_single(print_key_str, item.old, "Removed", output, comparer_set[D.DiffType.old], trace)
            else:
                current_length += 1
                if comparer_set[D.DiffType.not_diff] is None:
                    if self.print_all:
                        new_trace = trace.copy(self.name, index)
                        output.extend(self.print_item(index, item, self.check_printer_output(comparer_set.print_text(D.DiffType.not_diff, item, new_trace), new_trace), message="Unchanged "))
                    pass # This means that it is not a Diff and does not contains Diffs, so there is no text to write.
                else:
                    new_trace = trace.copy(self.name, index)
                    subcomparer_lines, has_changes = self.check_comparer_output(comparer_set.compare_text(D.DiffType.not_diff, item, new_trace), new_trace)
                    if has_changes:
                        any_changes = True
                        if self.ordered:
                            output.append("Changed %s %i:" % (self.name, index))
                        else:
                            output.append("Changed %s:" % (self.name))
                        output.extend("\t" + line for line in subcomparer_lines)
                    elif self.print_all:
                        output.extend(self.print_item(index, item, self.check_printer_output(comparer_set.print_text(D.DiffType.not_diff, item, new_trace), new_trace), message="Unchanged "))
        if self.measure_length and size_changed:
            output = ["Total %s: %i (+%i, -%i)" % (self.name, current_length, addition_length, removal_length)] + output
        return output, any_changes

class TypedDictComparerSection(DictComparerSection[str,d]):
    def __init__(self, name:str, types:dict[str,dict[type,ComparerSection[d]|None]], measure_length:bool=False, print_all:bool=False) -> None:
        self.name = name
        self.types = types
        self.check_initialization_parameters()
        self.detect_key_moves = False
        self.measure_length = measure_length
        self.print_all = print_all

    def check_initialization_parameters(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("`name` is not a str!")
        if not isinstance(self.types, dict):
            raise TypeError("`types` is not a dict!")
        for index, (key, value) in enumerate(self.types.items()):
            if not isinstance(key, str):
                raise TypeError("Key number %i of `types` is not a str, but instead %s!" % (index, key.__class__.__name__))
            if not isinstance(value, dict):
                raise TypeError("Value of key \"%s\" of `types` is not a dict, but instead %s!" % (key, value.__class__.__name__))
            for sub_index, (sub_key, sub_value) in enumerate(value.items()):
                if not isinstance(sub_key, type):
                    raise TypeError("Key number %i of value of key \"%s\" of `types` is not a type, but instead %s!" % (sub_index, key, sub_key.__class__.__name__))
                if not (sub_value is None or isinstance(sub_value, ComparerSection)):
                    raise TypeError("Value of key \"%s\" of value of key \"%s\" of `types` is not a ComparerSection or None, but instead %s!" % (sub_key, key, sub_value.__class__.__name__))

    def check_types(self, data:dict[str,d], trace:Trace) -> list[tuple[Trace,Exception]]:
        '''Recursively checks if the types are correct. Should not be given data containing Diffs.'''
        output:list[tuple[Trace,Exception]] = []
        if not isinstance(data, dict):
            output.append((trace, TypeError("`data` has the wrong type, %s instead of dict!" % (type(data)))))
            return output
        for key, value in data.items():
            new_trace = trace.copy(self.name, key)
            if isinstance(key, D.Diff) or isinstance(value, D.Diff):
                raise TypeError("`check_types` was given data containg Diffs!")

            if key not in self.types:
                output.append((new_trace.copy().give_key(self.name), TypeError("Key, value %s: %s in %s excepted because key is not recognized!" % (stringify(key), stringify(value), self.name))))
                continue
            if type(value) not in self.types[key]:
                value_types_string = ", ".join(type_key.__name__ for type_key in self.types[key])
                output.append((new_trace.copy().give_key(self.name), TypeError("Key, value %s: %s in %s excepted because value is %s instead of [%s]!" % (stringify(key), stringify(value), self.name, value_types_string))))
                continue

            comparer_set = self.choose_comparer(key, value)
            if len(comparer_set) != 1 or D.DiffType.not_diff not in comparer_set:
                raise TypeError("`check_types` was given data containg Diffs!")
            comparer = comparer_set[D.DiffType.not_diff]
            if comparer is not None:
                output.extend(comparer.check_types(value, new_trace))
        return output
    
    def choose_comparer(self, key:str, value:d) -> ComparerSet:
        output:dict[D.DiffType,ComparerSection] = {}
        for key_iter, value_iter, key_diff_type, value_diff_type in D.double_iter_diff(key, value):
            output[value_diff_type] = self.types[key_iter][type(value_iter)]
        return ComparerSet(output)

class Comparer():
    '''Can be created by a DataMinerCollection to compare the output of the DataMiners with each other.'''
    def __init__(self, name:str, normalizer:Callable[[a, "Version.Version", dict[str,"DataMiner.DataMinerCollection"]], b]|None, dependencies:list[str]|None, base_comparer_section:ComparerSection[b], post_normalizer:Callable[[a],b]|None=None) -> None:
        if not isinstance(name, str):
            raise TypeError("`name` is not a str!")
        if not isinstance(normalizer, (Callable, type(None))):
            raise TypeError("`normalizer` is not a Callable or None!")
        if not isinstance(post_normalizer, (Callable, type(None))):
            raise TypeError("`post_normalizer` is not a Callable or None!")
        if not isinstance(dependencies, (list, type(None))):
            raise TypeError("`dependencies` is not a list or None!")
        if isinstance(dependencies, list) and not all(isinstance(dependency, str) for dependency in dependencies):
            raise TypeError("An item of `dependencies` is not a str!")
        if not (isinstance(base_comparer_section, ComparerSection) or base_comparer_section is None):
            raise TypeError("`base_comparer_section` is not a ComparerSection!")

        self.name = name
        self.dependencies = [] if dependencies is None else dependencies
        if normalizer is None:
            self.normalizer = lambda data, version, dataminers: data
        else:
            self.normalizer = normalizer
        if post_normalizer is None:
            self.post_normalizer = lambda data: data
        else:
            self.post_normalizer = post_normalizer
        self.base_comparer_section = base_comparer_section

    def normalize(self, data:a, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> b:
        '''Manipulates the data before comparison.'''
        return self.normalizer(data, version, dataminers)

    def store(self, report:str) -> None:
        if self.name is None:
            raise RuntimeError("Attempted to store Comparer with uninitialized `name`!")
        if self.name in file_counts:
            store_number = file_counts[self.name] + 1
        else:
            store_number = 0
        comparison_path = FileManager.get_comparison_file_path(self.name, store_number)
        if not comparison_path.parent.exists():
            comparison_path.parent.mkdir()
        file_counts[self.name] = store_number
        with open(comparison_path, "wt") as f:
            f.write(report)

    def comparison_report(self, data1, data2:b, version1:Union["Version.Version",None], version2:"Version.Version", versions_between:list["Version.Version"], all_dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> tuple[str,bool]:
        '''Returns a final string of the comparison report and a boolean if there were any changes.'''
        if self.name is None:
            raise RuntimeError("Attempted to create comparison report using Comparer with uninitialized `name`!")
        header:list[str] = []
        beta_texts:list[str] = ["", ""]
        for index, version in enumerate((version1, version2)):
            if version is not None and version.ordering_tag is VersionTags.VersionTag.beta:
                beta_texts[index] = " (beta of \"%s\")" % version.parent.name
        if version1 is None:
            header.append("Addition of \"%s\"%s at \"%s\"%s." % (self.name, beta_texts[0], version2.name, beta_texts[1]))
        else:
            header.append("Difference of \"%s\" between \"%s\"%s and \"%s\"%s." % (self.name, version1.name, beta_texts[0], version2.name, beta_texts[1]))
        if len(versions_between) > 0:
            files_word = "file" if len(versions_between) == 1 else "files"
            between_word = "before" if version1 is None else "between"
            if len(versions_between) > 10:
                header.append("Unable to create data %s for %i files %s." % (files_word, len(versions_between), between_word))
            elif len(versions_between) <= 10:
                header.append("Unable to create data files for %i %s %s: %s" % (len(versions_between), files_word, between_word, ", ".join("\"%s\"" % version.name for version in versions_between)))
        header.append("")

        if version1 is None:
            normalized_data2 = self.normalize(data2, version2, all_dataminers)
            self.check_types(normalized_data2)
            normalized_data1 = type(normalized_data2)() # create new empty.
        else:
            normalized_data1 = self.normalize(data1, version1, all_dataminers)
            normalized_data2 = self.normalize(data2, version2, all_dataminers)
            self.check_types(normalized_data1)
            self.check_types(normalized_data2)

        data_comparison = self.compare(normalized_data1, normalized_data2)

        comparer_output = self.compare_text(data_comparison)
        if not isinstance(comparer_output, tuple):
            raise RuntimeError("Base comparer of \"%s\" did not return a tuple, but instead %s!" % (self.name, type(comparer_output)))
        lines, any_changes = comparer_output

        final = header
        final.extend(lines)

        return "\n".join(final), any_changes

    def check_types(self, data:b) -> None:
        '''Raises an exception with data about what went wrong if an error occurs.'''
        if self.base_comparer_section is None:
            raise RuntimeError("`base_comparer_section` was never initialized!")
        traces = self.base_comparer_section.check_types(data, Trace())
        if isinstance(self, DefaultComparer): return
        for trace, exception in traces:
            print("Exception in %s:" % trace)
            traceback.print_exception(exception)
            # raise exception
            print()
        if len(traces) > 0:
            raise RuntimeError("An error occured!")
        if len(traces) > 0:
            raise TypeError("Type checking on %s failed!" % (self.name))

    def compare(self, data1:b, data2:b) -> b:
        if self.base_comparer_section is None:
            raise RuntimeError("`base_comparer_section` was never initialized!")
        return self.base_comparer_section.compare(data1, data2, Trace())

    def compare_text(self, data:b) -> tuple[list[str],bool]:
        '''Returns a list of lines and if there were any changes'''
        if self.base_comparer_section is None:
            raise RuntimeError("`base_comparer_section` was never initialized!")
        return self.base_comparer_section.compare_text(data, Trace())

    def print_text(self, data:b) -> list[str]:
        if self.base_comparer_section is None:
            raise RuntimeError("`base_comparer_section` was never initialized!")
        return self.base_comparer_section.print_text(data, Trace())

class DefaultComparer(Comparer):
    def __init__(self) -> None:
        super().__init__("default", None, None, ComparerSection(""))

default_comparer = DefaultComparer()
#TODO: change check_types to a generator.