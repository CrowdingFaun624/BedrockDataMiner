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
def stringify_trace(trace:list[tuple[str,str]], name:str|None=None) -> str:
    if name is None:
        return ".".join("%s[%s]" % (name, index) for name, index in trace)
    else:
        if len(trace) == 0:
            return name
        else:
            return ".".join("%s[%s]" % (name, index) for name, index in trace) + ".%s" % (name)

class ComparerSection(Generic[a]):
    def __init__(self, name:str) -> None:
        if not isinstance(name, str):
            raise TypeError("`name` is not a str!")
        self.name = name
    
    def __repr__(self) -> str:
        return "<ComparerSection %s>" % self.name

    def print_single(self, key_str:str|None, data:d, message:str, output:list[str], printer:Union["ComparerSection[d]",None], trace:list[tuple[str,str]]) -> None:
        if printer is None:
            stringified_data = stringify(data)
            if key_str is None:
                output.append("%s %s %s." % (message, self.name, stringified_data))
            else:
                output.append("%s %s %s of %s." % (message, self.name, stringify(key_str), stringified_data))
        else:
            new_trace = trace.copy()
            new_trace.append((self.name, key_str))
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
    
    def print_double(self, key_str:str|None, data1:d, data2:d, message:str, output:list[str], printers:"ComparerSet", trace:list[tuple[str,str]]) -> None:
        new_trace = trace.copy()
        new_trace.append((self.name, key_str))
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

    def check_comparer_output(self, output:a, trace:list[tuple[str,str]]) -> a:
        if not isinstance(output, tuple):
            raise TypeError("%s did not return a tuple!" % (stringify_trace(trace, self.name)))
        if len(output) != 2:
            raise ValueError("%s did not return a tuple with length 2!" % (stringify_trace(trace, self.name)))
        if not isinstance(output[0], list):
            raise TypeError("The first item of the return of %s is not a list!" % (stringify_trace(trace, self.name)))
        if not isinstance(output[1], bool):
            raise TypeError("The second item of the return of %s is not a bool!" % (stringify_trace(trace, self.name)))
        if output[1] is True and len(output[0]) == 0:
            raise ValueError("The first item of the return of %s is empty and should not be!" % (stringify_trace(trace, self.name)))
        if not all(isinstance(line, str) for line in output[0]):
            raise TypeError("An item of the first item of the return of %s is not a str!" % (stringify_trace(trace, self.name)))
        return output
    
    def check_printer_output(self, output:a, trace:list[tuple[str,str]]) -> a:
        if not isinstance(output, list):
            raise TypeError("%s did not return a list!" % (stringify_trace(trace, self.name)))
        if not all(isinstance(line, str) for line in output):
            raise TypeError("An item of the return value of %s is not a str!" % (stringify_trace(trace, self.name)))
        return output

    def check_types(self, data:a, trace:list[tuple[str,str]]) -> list[tuple[list[tuple[str,str]], Exception]]: ...
    def compare_text(self, data:a, trace:list[tuple[str,str]]) -> tuple[list[str],bool]: ...
    def print_text(self, data:a, trace:list[tuple[str,str]]) -> list[str]: ...
    def compare(self, data1:a, data2:a, trace:list[tuple[str,str]]) -> a: ...

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
    def print_text(self, key:D.DiffType|int, data:d, trace:list[tuple[str,str]]) -> list[str]:
        comparer = self[key]
        if comparer is None:
            return [stringify(data)]
        else:
            return comparer.print_text(data, trace)
    def compare_text(self, key:D.DiffType|int, data:d, trace:list[tuple[str,str]]) -> tuple[list[str],bool]:
        comparer = self[key]
        if comparer is None:
            raise RuntimeError("Attempted to compare (key %s) using a NoneType object at %s!" % (key, stringify_trace(trace)))
        else:
            return comparer.compare_text(data, trace)
    def compare(self, data1:d, data2:d, trace:list[tuple[str,str]]) -> d:
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
            comparer:ComparerSection[d]|None|list[tuple[Callable[[c, d],bool]|str,ComparerSection[d]|None]],
            key_types:tuple[type]|Callable[[c, d],bool]|None,
            value_types:tuple[type]|Callable[[c, d],bool]|None,
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
        if not isinstance(name, str):
            raise TypeError("`name` is not a str!")
        if not isinstance(comparer, (ComparerSection, type(None), list)):
            raise TypeError("`comparer` is not a ComparerSection, NoneType, or list!")
        if isinstance(comparer, list):
            if not all(isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], (Callable, str)) and isinstance(item[1], (ComparerSection, type(None))) for item in comparer):
                raise TypeError("`comparer` is not a list of tuples of Callables and ComparerSections!")
        for name_types, types in (("key_types", key_types), ("value_types", value_types)):
            if isinstance(types, type) or (not isinstance(types, (tuple, Callable)) and types is not None):
                raise TypeError("`%s` is not an Iterable, Callable, or None!" % (name_types))
            if isinstance(types, tuple) and not all(isinstance(item, (type)) for item in types):
                raise TypeError("An item of `%s` is not a type!" % (name_types))
        if not isinstance(detect_key_moves, bool):
            raise TypeError("`detect_key_moves` is not a bool!")
        if not isinstance(comparison_move_function, Callable) and comparison_move_function is not None:
            raise TypeError("`comparison_move_function` is not a Callable or None!")
        if not isinstance(measure_length, bool):
            raise TypeError("`measure_length` is not a bool!")
        if not isinstance(print_all, bool):
            raise TypeError("`print_all` is not a bool!")
        
        self.name = name
        self.comparer = comparer
        self.key_types = (object,) if key_types is None else key_types
        self.value_types = (object,) if value_types is None else value_types
        self.detect_key_moves = detect_key_moves
        self.comparison_move_function = (lambda key, value: value) if comparison_move_function is None else comparison_move_function
        self.measure_length = measure_length
        self.print_all = print_all

    def check_types(self, data:dict[c,d], trace:list[tuple[str,str]]) -> list[tuple[list[tuple[str,str]],Exception]]:
        '''Recursively checks if the types are correct. Should not be given data containing Diffs.'''
        output:list[list[tuple[str,str]]] = []
        if not isinstance(data, dict):
            output.append((trace, TypeError("`data` has the wrong type, %s instead of dict!" % type(data))))
            return output
        for key, value in data.items():
            new_trace = trace.copy()
            new_trace.append((self.name, key))
            if isinstance(key, D.Diff) or isinstance(value, D.Diff):
                raise TypeError("`check_types` was given data containg Diffs!")
            
            excepted = False
            for label, item, types in (("key", key, self.key_types), ("value", value, self.value_types)):
                if isinstance(types, tuple):
                    if not isinstance(item, types):
                        excepted = True
                        output.append((new_trace, TypeError("Key, value %s: %s in %s excepted because %s is not %s!" % (stringify(key), stringify(value), self.name, label, types))))
                        break
                else:
                    try:
                        types_output = types(key, value)
                    except Exception as e:
                        excepted = True
                        types_output = None
                        arguments = list(e.args)
                        arguments.append("Type checker of %s for %s in key, value %s: %s excepted!" % (label, self.name, stringify(key), stringify(value)))
                        e.args = tuple(arguments)
                        output.append((new_trace, e))
                        break
                    if types_output is not True:
                        excepted = True
                        output.append((new_trace, TypeError("Type checker of %s for %s in key, value %s: %s returned False!" % (label, self.name, stringify(key), stringify(value)))))
                        break
            if excepted:
                continue
                
            comparer_set = self.choose_comparer(key, value, trace)
            if len(comparer_set) != 1 or D.DiffType.not_diff not in comparer_set:
                raise TypeError("`check_types` was given data containg Diffs!")
            comparer = comparer_set[D.DiffType.not_diff]
            if comparer is not None:
                output.extend(comparer.check_types(value, new_trace))
        return output

    def compare(self, data1: dict[c,d], data2: dict[c,d], trace:list[tuple[str,str]]) -> dict[c|D.Diff[c,c],d|D.Diff[d,d]]:
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
                    comparer_set = self.choose_comparer(key, D.Diff(value1, value2), trace)
                    new_trace = trace.copy()
                    new_trace.append((self.name, key))
                    output[key] = comparer_set.compare(value1, value2, new_trace)
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

    def choose_comparer(self, key:c, value:d, trace:list[tuple[str,str]]) -> ComparerSet:
        def lambda_test_value(test_function:Callable[[c,d],bool], test_key:c, test_value:d) -> bool:
            exception = None
            try:
                test_value_output = test_function(test_key, test_value)
            except Exception as e:
                exception_args = list(e.args)
                exception_args.append("Test function \"%s\" on \"%s\" for %s excepted!" % (test_function, test_key, stringify_trace(trace, self.name)))
                e.args = tuple(exception_args)
                exception = e
            if exception is not None: raise exception
            if not isinstance(test_value_output, bool):
                raise TypeError("Test function \"%s\" on \"%s\" for %s failed!" % (test_function, test_key, stringify_trace(trace, self.name)))
            return test_value_output
        
        output:dict[D.DiffType,ComparerSection] = {}
        for key_iter, value_iter, key_diff_type, value_diff_type in D.double_iter_diff(key, value):
            if isinstance(self.comparer, list):
                for test_function, new_comparer in self.comparer:
                    if (isinstance(test_function, str) and key_iter == test_function) or (isinstance(test_function, Callable) and lambda_test_value(test_function, key_iter, value_iter)):
                        output[value_diff_type] = new_comparer
                        break
                    else: continue
                else:
                    raise KeyError("Unable to find a ComparerSection for %s %s: %s!" % (stringify_trace(trace, self.name), stringify(key_iter), stringify(value_iter)))
            else:
                output[value_diff_type] = self.comparer
        return ComparerSet(output)

    def print_item(self, key:c, value:d, comparer_set:ComparerSet[d], trace:list[tuple[str,str]], message:str="") -> list[str]:
        new_trace = trace.copy()
        new_trace.append((self.name, key))
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

    def print_text(self, data:dict[c, d], trace:list[tuple[str,str]]) -> list[str]:
        output:list[str] = []
        if not isinstance(data, dict):
            raise TypeError("`data` is not a dict at %s, but instead type %s!" % (stringify_trace(trace, self.name), type(data)))
        for key, value in data.items():
            comparer_set = self.choose_comparer(key, value, trace)
            output.extend(self.print_item(key, value, comparer_set, trace))
        return output

    def compare_text(self, data:dict[c, d], trace:list[tuple[str,str]]) -> tuple[list[str],bool]:
        output:list[str] = []
        any_changes = False
        if not isinstance(data, dict):
            raise TypeError("`data` is not a dict at %s, but instead type %s!" % (stringify_trace(trace, self.name), type(data)))
        current_length, addition_length, removal_length = 0, 0, 0
        size_changed = False
        for key, value in data.items():
            can_print_print_all = True # if the print_all thing is overridden for whatever reason.
            key_str = key.first_existing_property() if isinstance(key, D.Diff) else key
            comparer_set = self.choose_comparer(key, value, trace)

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
                    new_trace = trace.copy()
                    new_trace.append((self.name, key_str))
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
            comparer:ComparerSection[d]|None|list[tuple[Callable[[int, d],bool],ComparerSection[d]|None]],
            types:tuple[type]|Callable[[int, c],bool]|None,
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
        if not isinstance(name, str):
            raise TypeError("`name` is not a str!")
        if isinstance(comparer, list):
            if not all(isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], Callable) and isinstance(item[1], (ComparerSection)) or item[1] is None for item in comparer):
                raise TypeError("`comparer` is not a list of tuples of Callables and ComparerSections!")
        if isinstance(types, type) or (not isinstance(types, (tuple, Callable)) and types is not None):
            raise TypeError("`types` is not an Iterable, Callable, or None but instead a \"%s\"!" % types.__class__.__name__)
        if isinstance(types, tuple) and not all(isinstance(item, (type, UnionType)) for item in types):
            raise TypeError("An item of `types` is not a type!")
        if not isinstance(print_flat, bool):
            raise TypeError("`print_flat` is not a bool!")
        if not isinstance(measure_length, bool):
            raise TypeError("`measure_length` is not a bool!")
        if not isinstance(print_all, bool):
            raise TypeError("`print_all` is not a bool!")

        self.name = name
        self.comparer = comparer
        self.types = [object] if types is None else types
        self.print_flat = print_flat
        self.ordered = ordered
        self.measure_length = measure_length
        self.print_all = print_all
    
    def check_types(self, data:list[d], trace:list[tuple[str,str]]) -> list[tuple[list[tuple[str,str]],Exception]]:
        '''Recursively checks if the types are correct. Should not be given data containing Diffs.'''
        output:list[list[tuple[int,d]]] = []
        for index, item in enumerate(data):
            new_trace = trace.copy()
            new_trace.append((self.name, index))
            if isinstance(item, D.Diff):
                raise TypeError("`check_types` was given data containg Diffs!")
            
            if isinstance(self.types, tuple):
                if not isinstance(item, self.types):
                    output.append((new_trace, TypeError("Index, item %i: %s in %s excepted because item is not %s!" % (index, stringify(item), self.name, self.types))))
                    continue
            else:
                try:
                    types_output = self.types(index, item)
                except Exception as e:
                    types_output = None
                    arguments = list(e.args)
                    arguments.append("Type checker for %s in index, item %i: %s excepted!" % (self.name, index, stringify(item)))
                    e.args = tuple(arguments)
                    output.append(new_trace)
                    continue
                if types_output is not True:
                    output.append((new_trace, TypeError("Type checker for %s in index, item %i: %s returned False!" % (self.name, index, stringify(item)))))
                    continue
                
            comparer_set = self.choose_comparer(index, item, trace)
            if len(comparer_set) != 1 or D.DiffType.not_diff not in comparer_set:
                raise TypeError("`check_types` was given data containg Diffs!")
            comparer = comparer_set[D.DiffType.not_diff]
            if comparer is not None:
                output.extend(comparer.check_types(item, new_trace))
        return output
    
    def compare(self, data1:Iterable[d], data2:Iterable[d], trace:list[tuple[str,str]]) -> Iterable[d]:
        output:list[d|D.Diff[d]] = []
        if self.ordered:
            index = -1
            for index, (item1, item2) in enumerate(zip(data1, data2)):
                if item1 == item2:
                    output.append(item1)
                else:
                    comparer_set = self.choose_comparer(index, D.Diff(item1, item2), trace)
                    new_trace = trace.copy()
                    new_trace.append((self.name, index))
                    output.append(comparer_set.compare(item1, item2, new_trace))
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
    
    def choose_comparer(self, index:int, item:d, trace:list[tuple[str,str]]) -> ComparerSet:
        output:dict[D.DiffType,ComparerSection] = {}
        for item_iter, diff_type in D.iter_diff(item):
            if isinstance(self.comparer, list):
                for test_value, new_comparer in self.comparer:
                    test_value_output = test_value(index, item_iter)
                    if not isinstance(test_value_output, bool):
                        raise TypeError("Test value \"%s\" on \"%s\" for %s failed!" % (test_value, item_iter, stringify_trace(trace, self.name)))
                    if test_value_output:
                        output[diff_type] = new_comparer
                        break
                    else: continue
                else:
                    raise KeyError("Unable to find a ComparerSection for %s %s!" % (stringify_trace(trace, self.name), str(item_iter)))
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

    def print_text(self, data:Iterable[d], trace:list[tuple[str,str]]) -> list[str]:
        output:list[str] = []
        items_str:list[str] = [] # print_flat only
        if not isinstance(data, Iterable):
            raise TypeError("`data` is not an Iterable at %s, but instead type %s!" % (stringify_trace(trace, self.name), type(data)))
        for index, item in enumerate(data):
            comparer_set = self.choose_comparer(index, item, trace)

            new_trace = trace.copy()
            new_trace.append((self.name, str(index)))
            subcomparer_output = self.check_printer_output(comparer_set.print_text(D.DiffType.not_diff, item, new_trace), new_trace)
            if self.print_flat:
                if len(subcomparer_output) == 1:
                    items_str.append(subcomparer_output[0])
                else:
                    raise RuntimeError("Subcomparer of flat-printing %s returned multiple lines!" % (stringify_trace(trace, self.name)))
            else:
                output.extend(self.print_item(index, item, subcomparer_output))
        if self.print_flat:
            output.append("[" + ", ".join(items_str) + "]")
        return output

    def compare_text(self, data:Iterable[d], trace:list[tuple[str,str]]) -> tuple[list[str],bool]:
        output:list[str] = []
        any_changes = False
        if not isinstance(data, Iterable):
            raise TypeError("`data` is not an Iterable at %s, but instead type %s!" % (stringify_trace(trace, self.name), type(data)))
        current_length, addition_length, removal_length = 0, 0, 0
        size_changed = False
        for index, item in enumerate(data):
            comparer_set = self.choose_comparer(index, item, trace)

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
                        new_trace = trace.copy()
                        new_trace.append((self.name, str(index)))
                        output.extend(self.print_item(index, item, self.check_printer_output(comparer_set.print_text(D.DiffType.not_diff, item, new_trace), new_trace), message="Unchanged "))
                    pass # This means that it is not a Diff and does not contains Diffs, so there is no text to write.
                else:
                    new_trace = trace.copy()
                    new_trace.append((self.name, str(index)))
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

def get_TypedDictComparerSection_attributes(
        name:str,
        types:list[tuple[str|list[str], type|tuple[type], ComparerSection[d]|None|list[tuple[Callable[[c,d],bool]|type|tuple[type], ComparerSection[d]|None]]]],
        ) -> tuple[Callable[[str,Any],bool,], Callable[[str,Any],bool], list[tuple[str,Callable[[c,d],bool], ComparerSection]]]:
    def get_func(comparer_key:str|Callable[[c],bool], additional_function:Callable[[c,d],bool]|type|tuple[type]) -> Callable[[c,d],bool]:
        if isinstance(additional_function, (tuple, type)):
            if isinstance(comparer_key, str):
                return lambda key, value: comparer_key == key and isinstance(value, additional_function)
            else:
                return lambda key, value: comparer_key(key, value) and isinstance(value, additional_function)
        else:
            if isinstance(comparer_key, str):
                return lambda key, value: comparer_key == key and additional_function(key, value)
            else:
                return lambda key, value: comparer_key(key, value) and additional_function(key, value)

    expanded_types:list[tuple[str|list[str], type|tuple[type], ComparerSection[d]|None|list[tuple[Callable[[c,d],bool]|type|tuple[type], ComparerSection[d]|None]]]] = []
    # `expanded_types` is just like `types`, but the first item is always a string.
    for keys, value_types, comparers in types:
        if isinstance(keys, list):
            expanded_types.extend((key, value_types, comparers) for key in keys)
        else:
            expanded_types.append((keys, value_types, comparers))
    keys_strings = {key for key, value_types, comparers in expanded_types if isinstance(key, str)}

    value_types_string_dict = {key: value_types for key, value_types, comparers in expanded_types}
    all_comparers:list[tuple[str,Callable[[c,d],bool], ComparerSection]] = []
    for comparer_key, value_types, comparers in expanded_types:
        if isinstance(comparers, ComparerSection) or comparers is None:
            all_comparers.append((comparer_key, comparers))
        else:
            for additional_function, comparer in comparers:
                all_comparers.append((get_func(comparer_key, additional_function), comparer))
    return (
        lambda key, value: key in keys_strings,
        lambda key, value: (key in value_types_string_dict and isinstance(value, value_types_string_dict[key])),
        all_comparers,
    )

def type_check_TypedDictComparerSection_parameters(
    name:str,
    types:list[tuple[str|list[str], type|tuple[type], ComparerSection[d]|None|list[tuple[Callable[[c,d],bool]|type|tuple[type], ComparerSection[d]|None]]]],
) -> None:
    if not isinstance(name, str):
        raise TypeError("`name` is not a str!")
    if not isinstance(types, (list, tuple)):
        raise TypeError("`types` is not a list or tuple!")
    already_keys:set[str] = set()
    for index, item in enumerate(types):
        if not isinstance(item, (tuple, list)):
            # It is allowed to be a list so that it can be changed to allow for nesting.
            raise TypeError("Item %i of `types` is not a tuple: %s" % (index, item))
        if len(item) != 3:
            raise ValueError("Item %i of `types` is not length 3: %s" % (index, item))
        if not isinstance(item[0], (str, list)):
            raise TypeError("The first item of item %i of `types` is not a str or list!" % (index,))
        if isinstance(item[0], list) and not all(isinstance(key, str) for key in item[0]):
            raise TypeError("An item of the first item of item %i of `types` is not a str!" % (index,))
        if (isinstance(item[0], str) and item[0] in already_keys) or (isinstance(item[0], list) and any(key in already_keys for key in item[0])):
            raise ValueError("The first item of item %i of `types` is the same as another first item of an item of `types`!" % (index,))
        if isinstance(item[0], list):
            already_keys.update(item[0])
        else:
            already_keys.add(item[0])
        if not isinstance(item[1], (type, UnionType, tuple)):
            raise TypeError("The second item of item %i of `types` is not a type or tuple, but instead a %s!" % (index, item[1].__class__.__name__))
        if isinstance(item[1], tuple) and not all(isinstance(types_item, (type, UnionType)) for types_item in item[1]):
            raise TypeError("An item of the second item of item %i of `types` is not a type!" % (index,))
        if not isinstance(item[2], (ComparerSection, list)) and item[2] is not None:
            raise TypeError("The third item of item %i of `types` is not a ComparerSection, list, or None!" % (index,))
        if isinstance(item[2], list):
            if len(item[2]) == 0:
                raise ValueError("The third item of item %i of `types` is empty!" % (index,))
            for comparer_item_index, comparer_item in enumerate(item[2]):
                if not isinstance(comparer_item, (list, tuple)):
                    raise TypeError("Item %i of the third item of item %i of `types` is not a list or tuple!" % (comparer_item_index, index))
                if len(comparer_item) != 2:
                    raise ValueError("Item %i of the third item of item %i of `types` is not length 2!" % (index,))
                if not isinstance(comparer_item[0], (Callable, type, tuple)):
                    raise TypeError("The first item of item %i of the third item of item %i of `types` is not a Callable, type, or tuple!" % (comparer_item_index, index))
                if isinstance(comparer_item[0], tuple) and not all(isinstance(type_item, type) for type_item in comparer_item[0]):
                    raise TypeError("An item of the first item of item %i of the third item of item %i of `types` is not a type!" % (comparer_item_index, index))
                if not isinstance(comparer_item[1], ComparerSection) and comparer_item[1] is not None:
                    raise TypeError("The second item of item %i of the third item of item %i of `types` is not a ComparerSection or None!" % (comparer_item_index, index))

def TypedDictComparerSection(name:str, types:list[tuple[str|list[str], type|tuple[type], ComparerSection[d]|None|list[tuple[Callable[[c,d],bool]|type|tuple[type], ComparerSection[d]|None]]]], measure_length:bool=False) -> DictComparerSection[c,d]:
    '''Alias for a DictComparerSection that has certain named parameters.
    * `name` is what the key of this dictionary is.
    * `items` is a list of tuples describing the keys and values.
    * The first item of each tuple of `items` is the key value; it will match this value to the key.
    * If the first item of the tuple is a list, then it make the same comparer for all items of the list.
    * The second item of each tuple describes the allowed types of the value.
    * The third item of each tuple is the ComparerSection for the matched key and value.
    * If the third item of each tuple is a list, then it will call the first item of each tuple with the key and value, and use the corresponding ComparerSection.'''
    type_check_TypedDictComparerSection_parameters(name, types)
    key_types_lambda, value_types_lambda, all_comparers = get_TypedDictComparerSection_attributes(name, types)

    return DictComparerSection(
        name=name,
        key_types=key_types_lambda,
        value_types=value_types_lambda,
        comparer=all_comparers,
        measure_length=measure_length,
    )

def UnnamedDictComparerSection(
        *types:tuple[str|list[str],type|tuple[type], ComparerSection[d]|None|list[tuple[Callable[[c,d],bool], ComparerSection[d]|None]]],
        name:str="field",
        measure_length:bool=False
    ) -> DictComparerSection:
    return TypedDictComparerSection(
        name=name,
        measure_length=measure_length,
        types=types
    )

class Comparer():
    '''Can be created by a DataMinerCollection to compare the output of the DataMiners with each other.'''
    def __init__(self, normalizer:Callable[[a, "Version.Version", dict[str,"DataMiner.DataMinerCollection"]], b]|None, dependencies:list[str]|None, base_comparer_section:ComparerSection[b], post_normalizer:Callable[[a],b]|None=None) -> None:
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

        self.name = None
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
        traces = self.base_comparer_section.check_types(data, [])
        if isinstance(self, DefaultComparer): return
        for trace, exception in traces:
            print("Exception in %s:" % stringify_trace(trace))
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
        return self.base_comparer_section.compare(data1, data2, [])

    def compare_text(self, data:b) -> tuple[list[str],bool]:
        '''Returns a list of lines and if there were any changes'''
        if self.base_comparer_section is None:
            raise RuntimeError("`base_comparer_section` was never initialized!")
        return self.base_comparer_section.compare_text(data, [])
    
    def print_text(self, data:b) -> list[str]:
        if self.base_comparer_section is None:
            raise RuntimeError("`base_comparer_section` was never initialized!")
        return self.base_comparer_section.print_text(data, [])

class DefaultComparer(Comparer):
    def __init__(self) -> None:
        super().__init__(None, None, ComparerSection(""))

default_comparer = DefaultComparer()
#TODO: change check_types to a generator.