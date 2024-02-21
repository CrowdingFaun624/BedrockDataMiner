from types import UnionType
from typing import Iterable, TypeVar

import Comparison.ComparerSection as ComparerSection
import Comparison.ComparerSet as ComparerSet
import Comparison.ComparisonUtilities as CU
import Comparison.Difference as D
import Comparison.Normalizer as Normalizer
import Comparison.Trace as Trace

d = TypeVar("d")

class ListComparerSection(ComparerSection.ComparerSection[Iterable[d]]):

    def __init__(
            self,
            name:str,
            comparer:ComparerSection.ComparerSection[d]|None|dict[type,ComparerSection.ComparerSection[d]|None],
            types:tuple[type,...]|None,
            print_flat:bool=False,
            ordered:bool=True,
            measure_length:bool=False,
            print_all:bool=False,
            normalizer:list[Normalizer.Normalizer]|None=None,
            children_has_normalizer:bool=False,
        ) -> None:
        ''' * `name` is what the key of this list is.
         * If `comparer` is a ComparerSection, then it will compare and print all items using that ComparerSection.
         * If `comparer` is None, then it will use `stringify` in place of a printer and not compare.
         * If `comparer` is a dictionary with keys of tuples of types and values of ComparerSections or Nones, then it will use the type of each item to choose the comparer section.
         * `types` is a tuple of types. All items of this list must be one of those types.
         * If `print_flat` is True, then lists are printed such as [item1, item2, item3].
         * If `print_flat` is False: then lists are printed such as 0: item1\\n1: item2\\n2: item3
         * If `measure_length` is True, then it will show how the length of the data changed when comparing.
         * If `print_all` is True, then if there is a change in one part of the data, then all parts will be printed.
         * `normalizer` is a list of normalizer functions that modify the data without returning anything.'''

        self.name = name
        self.comparer = comparer
        self.types = [object] if types is None else types
        self.print_flat = print_flat
        self.ordered = ordered
        self.measure_length = measure_length
        self.print_all = print_all
        self.normalizer = normalizer
        self.children_has_normalizer = children_has_normalizer
        self.check_initialization_parameters()

    def check_initialization_parameters(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("`name` is not a str!")
        if not (self.comparer is None or isinstance(self.comparer, (ComparerSection.ComparerSection, dict))):
            raise TypeError("`comparer` is not a ComparerSection, dict, or None!")
        if isinstance(self.comparer, dict):
            for comparer_index, (comparer_key, comparer_value) in enumerate(self.comparer.items()):
                if not isinstance(comparer_key, type):
                    raise TypeError("Key number %i of `comparer` is not a type!" % (comparer_index))
                if not (comparer_value is None or isinstance(comparer_value, ComparerSection.ComparerSection)):
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
        if not (self.normalizer is None or isinstance(self.normalizer, list)):
            raise TypeError("`normalizer` is not a list or None!")
        if isinstance(self.normalizer, list) and len(self.normalizer) == 0:
            raise TypeError("`normalizer` is empty!")
        if isinstance(self.normalizer, list) and not all(isinstance(item, Normalizer.Normalizer) for item in self.normalizer):
            raise TypeError("An item of `normalizer` is not a Normalizer!")
        if not isinstance(self.children_has_normalizer, bool):
            raise TypeError("`children_has_normalizer` is not a bool!")

    def check_type(self, index:int, item:d, trace:Trace.Trace) -> tuple[Trace.Trace,Exception]|None:
        if isinstance(item, D.Diff):
            raise TypeError("`check_all_types` was given data containing Diffs!")
        if not isinstance(item, self.types):
            return (trace.copy(self.name, index), TypeError("Index, item %i: %s in %s excepted because item is not %s!" % (index, CU.stringify(item), self.name, self.types)))

    def check_all_types(self, data:list[d], trace:Trace.Trace) -> list[tuple[Trace.Trace,Exception]]:
        '''Recursively checks if the types are correct. Should not be given data containing Diffs.'''
        output:list[list[tuple[int,d]]] = []
        for index, item in enumerate(data):
            check_type_output = self.check_type(index, item, trace)
            if check_type_output is not None:
                assert check_type_output[0] is not None
                output.append(check_type_output)
                continue

            comparer_set = self.choose_comparer(index, item, trace)
            if len(comparer_set) != 1 or D.DiffType.not_diff not in comparer_set:
                raise TypeError("`check_all_types` was given data containing Diffs!")
            comparer = comparer_set[D.DiffType.not_diff]
            if comparer is not None:
                output.extend(comparer.check_all_types(item, trace.copy(self.name, index)))
        return output

    def normalize(self, data:Iterable[d], normalizer_dependencies:Normalizer.LocalNormalizerDependencies, version_number:int, trace:Trace.Trace) -> None:
        if not self.children_has_normalizer: return
        if self.normalizer is not None:
            for normalizer in self.normalizer:
                normalizer(data, normalizer_dependencies, trace, version_number)
        for index, item in enumerate(data):
            try:
                comparer_set = self.choose_comparer(index, item, trace)
            except Exception:
                # it hasn't been type checked yet, so something could except
                continue
            if len(comparer_set) != 1 or D.DiffType.not_diff not in comparer_set:
                raise TypeError("`normalize` was given data containing Diffs in %s in %s: %s. comparer set is %s; excepted on item %i: %s" % (self.name, trace, data, comparer_set, index, item))
            comparer = comparer_set[D.DiffType.not_diff]
            if comparer is not None:
                comparer.normalize(item, normalizer_dependencies, version_number, trace.copy(self.name, index))

    def compare(
            self,
            data1:Iterable[d],
            data2:Iterable[d],
            trace:Trace.Trace,
        ) -> tuple[Iterable[d],list[tuple[Trace.Trace,Exception]]]:
        exceptions:list[tuple[Trace.Trace,Exception]] = []

        output:list[d|D.Diff[d]] = []
        if self.ordered:
            index = -1
            for index, (item1, item2) in enumerate(zip(data1, data2)):
                # type exception handling
                if (check_type_exception := self.check_type(index, item1, trace)) is not None:
                    exceptions.append(check_type_exception)
                if (check_type_exception := self.check_type(index, item2, trace)) is not None:
                    exceptions.append(check_type_exception)

                if item1 == item2:
                    output.append(item1)
                else:
                    comparer_set = self.choose_comparer(index, D.Diff(item1, item2), trace)
                    compare_output, new_exceptions = comparer_set.compare(item1, item2, trace.copy(self.name, index))
                    output.append(compare_output)
                    exceptions.extend(new_exceptions)
            # now, only the shortest iterable has been consumed.
            if len(data1) != len(data2):
                if len(data1) > len(data2):
                    iterator = data1[index + 1:] # pls don't break
                    data1_is_bigger = True
                else:
                    iterator = data2[index + 1:]
                    data1_is_bigger = False
                for i, item in enumerate(iterator):
                    # index is end of shortest; i is the offset from that.
                    if (check_type_exception := self.check_type(index + i + 1, item, trace)) is not None:
                        exceptions.append(check_type_exception)
                    output.append((D.Diff(old=item) if data1_is_bigger else D.Diff(new=item)))
            else: pass
            return output, exceptions
        else: # unordered can only have additions or removals, no changes.
            for index, item in enumerate(data1):
                if (check_type_exception := self.check_type(index, item, trace)) is not None:
                    exceptions.append(check_type_exception)
                if item in data2:
                    output.append(item) # item in both
                else:
                    output.append(D.Diff(old=item))
            for index, item in enumerate(data2):
                if (check_type_exception := self.check_type(index, item, trace)) is not None:
                    exceptions.append(check_type_exception)
                if item in data1:
                    pass # ignore; already added.
                else:
                    output.append(D.Diff(new=item))
            return output, exceptions

    def choose_comparer(self, index:int, item:d, trace:Trace.Trace) -> ComparerSet.ComparerSet:
        output:dict[D.DiffType,ComparerSection.ComparerSection] = {}
        for item_iter, diff_type in D.iter_diff(item):
            if isinstance(self.comparer, dict):
                exception = None
                try:
                    output[diff_type] = self.comparer[type(item_iter)]
                except Exception as e:
                    exception = e
                    exception.args = tuple(list(exception.args) + ["Failed to get comparer at %s of item %i: %s" % (trace, index, item_iter)])
            else:
                output[diff_type] = self.comparer
        return ComparerSet.ComparerSet(output)

    def print_item(self, index:int, item:d, subcomparer_output:list[str], message:str="") -> list[str]:
        match len(subcomparer_output), self.ordered:
            case 0, True:
                return ["%s%s %i: empty" % (message, self.name, index)]
            case 0, False:
                return ["%s%s: empty" % (message, self.name)]
            case 1, True:
                return ["%s%s %i: %s" % (message, self.name, index, subcomparer_output[0])]
            case 1, False:
                return ["%s%s: %s" % (message, self.name, subcomparer_output[0])]
            case _:
                output:list[str] = []
                if self.ordered:
                    output.append("%s%s %i:" % (message, self.name, index))
                else:
                    output.append("%s%s:" % (message, self.name))
                output.extend("\t" + line for line in subcomparer_output)
                return output

    def print_text(self, data:Iterable[d], trace:Trace.Trace) -> list[str]:
        output:list[str] = []
        items_str:list[str] = [] # print_flat only
        if not isinstance(data, Iterable):
            raise TypeError("`data` is not an Iterable at %s, but instead type %s!" % (trace.give_key(self.name), type(data)))
        for index, item in enumerate(data):
            comparer_set = self.choose_comparer(index, item, trace)

            subcomparer_output = comparer_set.print_text(D.DiffType.not_diff, item, trace.copy(self.name, index))
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

    def compare_text(self, data:Iterable[d], trace:Trace.Trace) -> tuple[list[str],bool]:
        output:list[str] = []
        any_changes = False
        if not isinstance(data, Iterable):
            raise TypeError("`data` is not an Iterable at %s, but instead type %s!" % (trace, type(data)))
        current_length, addition_length, removal_length = 0, 0, 0
        size_changed = False
        for index, item in enumerate(data):
            comparer_set = self.choose_comparer(index, item, trace)

            if isinstance(item, D.Diff):
                any_changes = True
                print_key_str = index if self.ordered else None
                size_changed = True
                match item.change_type:
                    case D.ChangeType.addition:
                        current_length += 1; addition_length += 1
                        self.print_single(print_key_str, item.new, "Added", output, comparer_set[D.DiffType.new], trace)
                    case D.ChangeType.change:
                        current_length += 1
                        self.print_double(print_key_str, item.old, item.new, "Changed", output, comparer_set, trace)
                    case D.ChangeType.removal:
                        removal_length += 1
                        self.print_single(print_key_str, item.old, "Removed", output, comparer_set[D.DiffType.old], trace)
            else:
                current_length += 1
                if comparer_set[D.DiffType.not_diff] is None:
                    if self.print_all:
                        output.extend(self.print_item(index, item, comparer_set.print_text(D.DiffType.not_diff, item, trace.copy(self.name, index)), message="Unchanged "))
                    pass # This means that it is not a Diff and does not contains Diffs, so there is no text to write.
                else:
                    new_trace = trace.copy(self.name, index)
                    subcomparer_lines, has_changes = comparer_set.compare_text(D.DiffType.not_diff, item, new_trace)
                    if has_changes:
                        any_changes = True
                        if self.ordered:
                            output.append("Changed %s %i:" % (self.name, index))
                        else:
                            output.append("Changed %s:" % (self.name))
                        output.extend("\t" + line for line in subcomparer_lines)
                    elif self.print_all:
                        output.extend(self.print_item(index, item, comparer_set.print_text(D.DiffType.not_diff, item, new_trace), message="Unchanged "))
        if self.measure_length and size_changed:
            output = ["Total %s: %i (+%i, -%i)" % (self.name, current_length, addition_length, removal_length)] + output
        return output, any_changes
