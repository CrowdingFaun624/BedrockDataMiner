import json
from typing import Any, Callable, Generic, Iterable, TypeVar, TYPE_CHECKING, Union

import Comparison.Difference as D
import Utilities.FileManager as FileManager
import Utilities.VersionTags as VersionTags

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner
    import DataMiners.DataMinerTyping as DataMinerTyping

a = TypeVar("a")
b = TypeVar("b")
c = TypeVar("c", object, D.Diff)
d = TypeVar("d", object, D.Diff)

file_counts:dict[str,int] = {}

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
        return "<ComparerSet %s>" % self.name

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
            subcomparer_output = self.check_printer_output(printer.print(data, new_trace), new_trace)
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
        subcomparer_output1 = self.check_printer_output(printers.print(0, data1, new_trace), new_trace)
        subcomparer_output2 = self.check_printer_output(printers.print(-1, data2, new_trace), new_trace) # [-1] because it must be the last item anyways.
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

    def check_types(self) -> None: ...
    def compare(self, data:a, trace:list[tuple[str,str]]) -> tuple[list[str],bool]: ...
    def print(self, data:a, trace:list[tuple[str,str]]) -> list[str]: ...

class ComparerSet():
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

    def __getitem__(self, key:D.DiffType|int) -> ComparerSection|None:
        if isinstance(key, D.DiffType):
            return self.comparers[key]
        elif isinstance(key, int):
            return list(self.comparers.values())[key]
        else:
            raise KeyError("Attempted to index a ComparerSet using a %s rather than a D.DiffType!" % type(key))
    def print(self, key:D.DiffType|int, data:Any, trace:list[tuple[str,str]]) -> list[str]:
        comparer = self[key]
        if comparer is None:
            return [stringify(data)]
        else:
            return comparer.print(data, trace)
    def compare(self, key:D.DiffType|int, data:Any, trace:list[tuple[str,str]]) -> tuple[list[str],bool]:
        comparer = self[key]
        if comparer is None:
            raise RuntimeError("Attempted to compare (key %s) using a NoneType object at %s!" % (key, stringify_trace(trace)))
        else:
            return comparer.compare(data, trace)

class DictComparerSection(ComparerSection[dict[c, d]]):
    def __init__(self, name:str, comparer:ComparerSection[d]|None|list[tuple[Callable[[c, d],bool]|str,ComparerSection[d]|None]], key_types:tuple[type]|Callable[[c],bool]|None, value_types:tuple[type]|Callable[[d],bool]|None) -> None:
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
         * `key_types` or `value_types` is never given a D.Diff; Diffs are split into old and new and compared separately.'''
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
        
        self.name = name
        self.comparer = comparer
        self.key_types = (object,) if key_types is None else key_types
        self.value_types = (object,) if value_types is None else value_types

    def check_types(self, key:c, value:d, trace:list[tuple[str,str]]) -> None:
        '''Checks the types of every key and value, raising a TypeError if they do not match.'''
        def check_key(key:c, value:d) -> None:
            if isinstance(self.key_types, tuple):
                if not isinstance(key, self.key_types):
                    raise TypeError("Key \"%s\" is not an instance of %s on %s, instead type \"%s\"!" % (str(key), str(list(self.key_types), stringify_trace(trace, self.name), type(key))))
            else:
                try:
                    key_types_output = self.key_types(key, value)
                except Exception as e:
                    arguments = list(e.args)
                    arguments.append("Type checker excepted for key \"%s\" on %s!" % (stringify(key), stringify_trace(trace, self.name)))
                    e.args = tuple(arguments)
                    key_types_output = e
                if isinstance(key_types_output, Exception): raise key_types_output
                if not isinstance(key_types_output, bool):
                    raise TypeError("Type checker did not return a bool for key \"%s\" on %s!" % (stringify(key), stringify_trace(trace, self.name)))
                if key_types_output is False:
                    raise TypeError("Key \"%s\" has an invalid type on %s; the key's type is %s (value is %s)!" % (stringify(key), stringify_trace(trace, self.name), type(key), str(value)))
        def check_value(key:c, value:d) -> None:
            if isinstance(self.value_types, tuple):
                if not isinstance(value, self.value_types):
                    raise TypeError("The type of %s %s is not an instance of %s, instead type \"%s\"!" % (stringify_trace(trace, self.name), stringify(key), str(list(self.value_types)), type(value)))
            else:
                try:
                    value_types_output = self.value_types(key, value)
                except Exception as e:
                    arguments = list(e.args)
                    arguments.append("Type checker excepted for value of key %s on %s!" % (stringify(key_str), stringify_trace(trace, self.name)))
                    e.args = tuple(arguments)
                    value_types_output = e
                if isinstance(value_types_output, Exception): raise value_types_output
                if not isinstance(value_types_output, bool):
                    raise TypeError("Type checker did not return a bool for value of key %s on %s!" % (stringify(key_str), stringify_trace(trace, self.name)))
                if value_types_output is False:
                    raise TypeError("Value of key %s has an invalid type on %s; the value's type is \"%s\"!" % (stringify(key_str), stringify_trace(trace, self.name), type(value)))
        
        key_str = key.first_existing_property() if isinstance(key, D.Diff) else key
        for key_iter, value_iter, key_diff_type, value_diff_type in D.double_iter_diff(key, value):
            check_key(key_iter, value_iter)
            check_value(key_iter, value_iter)

    def choose_comparer(self, key:c, value:d, trace:list[tuple[str,str]]) -> ComparerSet:
        def lambda_test_value(test_function:Callable[[c,d],bool], test_key:c, test_value:d) -> bool:
            test_value_output = test_function(test_key, test_value)
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

    def print(self, data:dict[c, d], trace:list[tuple[str,str]]) -> list[str]:
        output:list[str] = []
        if not isinstance(data, dict):
            raise TypeError("`data` is not a dict at %s, but instead type %s!" % (stringify_trace(trace, self.name), type(data)))
        for key, value in data.items():
            comparer_set = self.choose_comparer(key, value, trace)
            self.check_types(key, value, trace)
            new_trace = trace.copy()
            new_trace.append((self.name, key))
            subcomparer_output = self.check_printer_output(comparer_set.print(D.DiffType.not_diff, value, new_trace), new_trace)
            if len(subcomparer_output) == 0:
                output.append("%s %s: empty" % (self.name, stringify(key)))
            elif len(subcomparer_output) == 1:
                output.append("%s %s: %s" % (self.name, stringify(key), subcomparer_output[0]))
            else:
                output.append("%s %s:" % (self.name, stringify(key)))
                output.extend("\t" + line for line in subcomparer_output)
        return output

    def compare(self, data:dict[c, d], trace:list[tuple[str,str]]) -> tuple[list[str],bool]:
        output:list[str] = []
        any_changes = False
        if not isinstance(data, dict):
            raise TypeError("`data` is not a dict at %s, but instead type %s!" % (stringify_trace(trace, self.name), type(data)))
        for key, value in data.items():
            key_str = key.first_existing_property() if isinstance(key, D.Diff) else key
            comparer_set = self.choose_comparer(key, value, trace)
            self.check_types(key, value, trace)

            if isinstance(key, D.Diff):
                if key.is_addition:
                    pass # Behavior is handled in the check for `value` being a `D.Diff`.
                elif key.is_change:
                    any_changes = True
                    output.append("Moved %s %s to %s." % (self.name, stringify(key.old), stringify(key.new)))
                elif key.is_removal:
                    pass # Behavior is handled in the check for `value` being a `D.Diff`.
            else:
                pass
            if isinstance(value, D.Diff):
                any_changes = True
                if value.is_addition:
                    self.print_single(key_str, value.new, "Added", output, comparer_set[D.DiffType.new], trace)
                elif value.is_change:
                    self.print_double(key_str, value.old, value.new, "Changed", output, comparer_set, trace)
                elif value.is_removal:
                    self.print_single(key_str, value.old, "Removed", output, comparer_set[D.DiffType.old], trace)
            else:
                if comparer_set[D.DiffType.not_diff] is None:
                    pass # This means that it is not a difference and does not contain differences.
                else:
                    new_trace = trace.copy()
                    new_trace.append((self.name, key_str))
                    subcomparer_lines, has_changes = self.check_comparer_output(comparer_set.compare(D.DiffType.not_diff, value, new_trace), new_trace)
                    if has_changes:
                        any_changes = True
                        output.append("Changed %s %s:" % (self.name, stringify(key_str)))
                        output.extend("\t" + line for line in subcomparer_lines)
        return output, any_changes

class ListComparerSection(ComparerSection[Iterable[d]]):
    def __init__(self, name:str, comparer:ComparerSection[d]|None|list[tuple[Callable[[int, d],bool],ComparerSection[d]|None]], types:tuple[type]|Callable[[int, c],bool]|None, print_flat:bool=False, ordered:bool=True) -> None:
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
         * If `print_flat` is False: then lists are printed such as 0: item1\\n1: item2\\n2: item3'''
        if not isinstance(name, str):
            raise TypeError("`name` is not a str!")
        if isinstance(comparer, list):
            if not all(isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], Callable) and isinstance(item[1], (ComparerSection)) or item[1] is None for item in comparer):
                raise TypeError("`comparer` is not a list of tuples of Callables and ComparerSections!")
        if isinstance(types, type) or (not isinstance(types, (tuple, Callable)) and types is not None):
            raise TypeError("`types` is not an Iterable, Callable, or None!")
        if isinstance(types, tuple) and not all(isinstance(item, (type)) for item in types):
            raise TypeError("An item of `types` is not a type!")
        if not isinstance(print_flat, bool):
            raise TypeError("`print_flat` is not a bool!")

        self.name = name
        self.comparer = comparer
        self.types = [object] if types is None else types
        self.print_flat = print_flat
        self.ordered = ordered
    
    def check_types(self, index:int, item:d, trace:list[tuple[str,str]]) -> None:
        if isinstance(item, D.Diff):
            if item.is_addition: items_iter = (item.new,)
            elif item.is_change: items_iter = (item.old, item.new)
            elif item.is_removal: items_iter = (item.old,)
        else: items_iter = (item,)
        for item_iter in items_iter:
            if isinstance(self.types, tuple):
                if not isinstance(item_iter, self.types):
                    raise TypeError("Item \"%s\" is not an instance of %s on %s, instead type \"%s\"!" % (str(item), str(list(self.types)), stringify_trace(trace, self.name), type(item)))
            else:
                types_output = self.types(index, item)
                if not isinstance(types_output, bool):
                    raise TypeError("Type checker did not return a bool for an item of %s!" % (stringify_trace(trace, self.name)))
                if types_output is False:
                    TypeError("Item \"%s\" has an invalid type on %s, instead type \"%s\"!" % (str(item), stringify_trace(trace, self.name), type(item_iter)))
    
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

    def print(self, data:Iterable[d], trace:list[tuple[str,str]]) -> list[str]:
        output:list[str] = []
        items_str:list[str] = [] # print_flat only
        if not isinstance(data, Iterable):
            raise TypeError("`data` is not an Iterable at %s, but instead type %s!" % (stringify_trace(trace, self.name), type(data)))
        for index, item in enumerate(data):
            comparer_set = self.choose_comparer(index, item, trace)
            self.check_types(index, item, trace)

            new_trace = trace.copy()
            new_trace.append((self.name, str(index)))
            subcomparer_output = self.check_printer_output(comparer_set.print(D.DiffType.not_diff, item, new_trace), new_trace)
            if self.print_flat:
                if len(subcomparer_output) == 1:
                    items_str.append(subcomparer_output[0])
                else:
                    raise RuntimeError("Subcomparer of flat-printing %s returned multiple lines!" % (stringify_trace(trace, self.name)))
            else:
                if len(subcomparer_output) == 0:
                    if self.ordered:
                        output.append("%s %i: empty" % (self.name, index))
                    else:
                        output.append("%s: empty" % (self.name))
                elif len(subcomparer_output) == 1:
                    if self.ordered:
                        output.append("%s %i: %s" % (self.name, index, subcomparer_output[0]))
                    else:
                        output.append("%s: %s" % (self.name, subcomparer_output[0]))
                else:
                    if self.ordered:
                        output.append("%s %i:" % (self.name, index))
                    else:
                        output.append("%s:" % (self.name))
                    output.extend("\t" + line for line in subcomparer_output)
        if self.print_flat:
            output.append("[" + ", ".join(items_str) + "]")
        return output

    def compare(self, data:Iterable[d], trace:list[tuple[str,str]]) -> tuple[list[str],bool]:
        output:list[str] = []
        any_changes = False
        if not isinstance(data, Iterable):
            raise TypeError("`data` is not an Iterable at %s, but instead type %s!" % (stringify_trace(trace, self.name), type(data)))
        for index, item in enumerate(data):
            comparer_set = self.choose_comparer(index, item, trace)
            self.check_types(index, item, trace)

            if isinstance(item, D.Diff):
                any_changes = True
                print_key_str = index if self.ordered else None
                if item.is_addition:
                    self.print_single(print_key_str, item.new, "Added", output, comparer_set[D.DiffType.new], trace)
                elif item.is_change:
                    self.print_double(print_key_str, item.old, item.new, "Changed", output, comparer_set, trace)
                elif item.is_removal:
                    self.print_single(print_key_str, item.old, "Removed", output, comparer_set[D.DiffType.old], trace)
            else:
                if comparer_set[D.DiffType.not_diff] is None:
                    pass # This means that it is not a Diff and does not contains Diffs.
                else:
                    new_trace = trace.copy()
                    new_trace.append((self.name, str(index)))
                    subcomparer_lines, has_changes = self.check_comparer_output(comparer_set.compare(D.DiffType.not_diff, item, new_trace), new_trace)
                    if has_changes:
                        any_changes = True
                        if self.ordered:
                            output.append("Changed %s %i:" % (self.name, index))
                        else:
                            output.append("Changed %s:" % (self.name))
                        output.extend("\t" + line for line in subcomparer_lines)
        return output, any_changes

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
        if not isinstance(base_comparer_section, ComparerSection):
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

    def comparison_report(self, data_comparison:b, version1:Union["Version.Version",None], version2:"Version.Version", versions_between:list["Version.Version"]) -> tuple[str,bool]:
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
        
        comparer_output = self.compare(data_comparison)
        if not isinstance(comparer_output, tuple):
            raise RuntimeError("Base comparer of \"%s\" did not return a tuple, but instead %s!" % (self.name, type(comparer_output)))
        lines, any_changes = comparer_output

        final = header
        final.extend(lines)

        return "\n".join(final), any_changes
    
    def compare(self, data:b) -> tuple[list[str],bool]:
        '''Returns a list of lines and if there were any changes'''
        return self.base_comparer_section.compare(data, [])
    
    def print(self, data:b) -> list[str]:
        return self.base_comparer_section.print(data, [])
