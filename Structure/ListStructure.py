from typing import Iterable, Sequence, TypeVar

import Structure.Structure as Structure
import Structure.StructureSet as StructureSet
import Structure.StructureUtilities as SU
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

d = TypeVar("d")

class ListStructure(Structure.Structure[Iterable[d]]):

    def __init__(
            self,
            name:str,
            structure:Structure.Structure[d]|None|dict[type,Structure.Structure[d]|None],
            types:tuple[type,...]|None,
            print_flat:bool,
            ordered:bool,
            measure_length:bool,
            print_all:bool,
            normalizer:list[Normalizer.Normalizer]|None,
            children_has_normalizer:bool,
        ) -> None:
        ''' * `name` is what the key of this list is.
         * If `structure` is a Structure, then it will compare and print all items using that Structure.
         * If `structure` is None, then it will use `stringify` in place of a printer and not compare.
         * If `structure` is a dictionary with keys of tuples of types and values of Structures or Nones, then it will use the type of each item to choose the Structure.
         * `types` is a tuple of types. All items of this list must be one of those types.
         * If `print_flat` is True, then lists are printed such as [item1, item2, item3].
         * If `print_flat` is False: then lists are printed such as 0: item1\\n1: item2\\n2: item3
         * If `measure_length` is True, then it will show how the length of the data changed when comparing.
         * If `print_all` is True, then if there is a change in one part of the data, then all parts will be printed.
         * `normalizer` is a list of normalizer functions that modify the data without returning anything.'''

        self.name = name
        self.structure = structure
        self.types = (object,) if types is None else types
        self.print_flat = print_flat
        self.ordered = ordered
        self.measure_length = measure_length
        self.print_all = print_all
        self.normalizer = normalizer
        self.children_has_normalizer = children_has_normalizer
        self.check_initialization_parameters()

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("structure", "a Structure, dict, or None", True, TypeVerifier.UnionTypeVerifier(
            "a Structure, dict, or None",
            type(None),
            Structure.Structure,
            TypeVerifier.DictTypeVerifier(dict, type, (type(None), Structure.Structure), "a dict", "a type", "a Structure or None")
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a tuple or None", True, TypeVerifier.UnionTypeVerifier("a tuple or None", type(None), TypeVerifier.ListTypeVerifier(type, tuple, "a type", "a tuple"))),
        TypeVerifier.TypedDictKeyTypeVerifier("print_flat", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("ordered", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a list or None", True, TypeVerifier.UnionTypeVerifier("a list or None", TypeVerifier.UnionTypeVerifier("a list or None", type(None), TypeVerifier.ListTypeVerifier(Normalizer.Normalizer, list, "a Normalizer", "a list", additional_function=lambda data: (len(data) > 0, "empty"))))),
        TypeVerifier.TypedDictKeyTypeVerifier("children_has_normalizer", "a bool", True, bool),
    )

    def check_initialization_parameters(self) -> None:
        self.type_verifier.base_verify({
            "name": self.name,
            "structure": self.structure,
            "types": self.types,
            "print_flat": self.print_flat,
            "ordered": self.ordered,
            "measure_length": self.measure_length,
            "print_all": self.print_all,
            "normalizer": self.normalizer,
            "children_has_normalizer": self.children_has_normalizer,
        })

    def check_type(self, index:int, item:d, trace:Trace.Trace) -> tuple[Trace.Trace,Exception]|None:
        if isinstance(item, D.Diff):
            raise TypeError("`check_all_types` was given data containing Diffs!")
        if not isinstance(item, self.types):
            item_types_string = ", ".join(type_key.__name__ for type_key in self.types)
            return (trace.copy(self.name, index), TypeError("Index, item %i: %s in %s excepted is %s instead of [%s]!" % (index, SU.stringify(item), self.name, item.__class__.__name__, item_types_string)))

    def check_all_types(self, data:list[d], trace:Trace.Trace) -> list[tuple[Trace.Trace,Exception]]:
        '''Recursively checks if the types are correct. Should not be given data containing Diffs.'''
        output:list[tuple[Trace.Trace,Exception]] = []
        for index, item in enumerate(data):
            check_type_output = self.check_type(index, item, trace)
            if check_type_output is not None:
                assert check_type_output[0] is not None
                output.append(check_type_output)
                continue

            structure = self.choose_structure_flat(index, type(item), trace)
            if structure is not None:
                output.extend(structure.check_all_types(item, trace.copy(self.name, index)))
        return output

    def normalize(self, data:list[d], normalizer_dependencies:Normalizer.LocalNormalizerDependencies, version_number:int, trace:Trace.Trace) -> None:
        if not self.children_has_normalizer: return
        if self.normalizer is not None:
            for normalizer in self.normalizer:
                normalizer(data, normalizer_dependencies, trace, version_number)
        for index, item in enumerate(data):
            try:
                structure = self.choose_structure_flat(index, type(item), trace)
            except Exception:
                # it hasn't been type checked yet, so something could except
                continue
            if structure is not None:
                normalize_output = structure.normalize(item, normalizer_dependencies, version_number, trace.copy(self.name, index))
                if normalize_output is not None:
                    data[index] = normalize_output

    def compare(
            self,
            data1:Sequence[d],
            data2:Sequence[d],
            trace:Trace.Trace,
        ) -> tuple[Sequence[d|D.Diff[d|D.NoExist,d|D.NoExist]],list[tuple[Trace.Trace,Exception]]]:
        if type(data1) != type(data2):
            raise TypeError("Attempted to compare type %s with type %s!" % (data1.__class__.__name__, data2.__class__.__name__))
        exceptions:list[tuple[Trace.Trace,Exception]] = []

        output:list[d|D.Diff[d|D.NoExist,d|D.NoExist]] = type(data1)() # type: ignore
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
                    structure_set = self.choose_structure(index, D.Diff(item1, item2), trace)
                    compare_output, new_exceptions = structure_set.compare(item1, item2, trace.copy(self.name, index))
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

    def choose_structure_flat(self, key:int, value:type[d], trace:Trace.Trace) -> Structure.Structure|None:
        if isinstance(self.structure, dict):
            exception = None
            try:
                return self.structure[value]
            except Exception as e:
                exception = e
                exception.args = tuple(list(exception.args) + ["Failed to get Structure at %s of item %i: %s" % (trace, key, value)])
            if exception is not None:
                raise exception
        else:
            return self.structure

    def choose_structure(self, index:int, item:d|D.Diff[d,d], trace:Trace.Trace) -> StructureSet.StructureSet:
        output:dict[D.DiffType,Structure.Structure|None] = {}
        for item_iter, diff_type in D.iter_diff(item):
            if isinstance(self.structure, dict):
                exception = None
                try:
                    output[diff_type] = self.structure[type(item_iter)]
                except Exception as e:
                    exception = e
                    exception.args = tuple(list(exception.args) + ["Failed to get Structure at %s of item %i: %s" % (trace, index, item_iter)])
                if exception is not None:
                    raise exception
            else:
                output[diff_type] = self.structure
        return StructureSet.StructureSet(output)

    def print_item(self, index:int, item:d, substructure_output:list[SU.Line], message:str="") -> list[SU.Line]:
        match len(substructure_output), self.ordered:
            case 0, True:
                return [SU.Line("%s%s %i: empty") % (message, self.name, index)]
            case 0, False:
                return [SU.Line("%s%s: empty") % (message, self.name)]
            case 1, True:
                return [SU.Line("%s%s %i: %s") % (message, self.name, index, substructure_output[0])]
            case 1, False:
                return [SU.Line("%s%s: %s") % (message, self.name, substructure_output[0])]
            case _:
                output:list[SU.Line] = []
                if self.ordered:
                    output.append(SU.Line("%s%s %i:") % (message, self.name, index))
                else:
                    output.append(SU.Line("%s%s:") % (message, self.name))
                output.extend(line.indent() for line in substructure_output)
                return output

    def print_text(self, data:Iterable[d], trace:Trace.Trace) -> list[SU.Line]:
        output:list[SU.Line] = []
        items_str:list[str] = [] # print_flat only
        if not isinstance(data, Iterable):
            raise TypeError("`data` is not an Iterable at %s, but instead type %s!" % (trace.give_key(self.name), type(data)))
        for index, item in enumerate(data):
            structure_set = self.choose_structure(index, item, trace)

            substructure_output = structure_set.print_text(D.DiffType.not_diff, item, trace.copy(self.name, index))
            if self.print_flat:
                if len(substructure_output) == 1:
                    items_str.append(substructure_output[0].text)
                else:
                    raise RuntimeError("Substructure of flat-printing %s returned multiple lines!" % (trace.give_key(self.name)))
            else:
                output.extend(self.print_item(index, item, substructure_output))
        if self.print_flat:
            output.append(SU.Line("[" + ", ".join(items_str) + "]"))
        return output

    def compare_text(self, data:Iterable[d], trace:Trace.Trace) -> tuple[list[SU.Line],bool]:
        output:list[SU.Line] = []
        any_changes = False
        if not isinstance(data, Iterable):
            raise TypeError("`data` is not an Iterable at %s, but instead type %s!" % (trace, type(data)))
        current_length, addition_length, removal_length = 0, 0, 0
        size_changed = False
        for index, item in enumerate(data):
            structure_set = self.choose_structure(index, item, trace)

            if isinstance(item, D.Diff):
                any_changes = True
                print_key_str = index if self.ordered else None
                size_changed = True
                match item.change_type:
                    case D.ChangeType.addition:
                        current_length += 1; addition_length += 1
                        self.print_single(print_key_str, item.new, "Added", output, structure_set[D.DiffType.new], trace)
                    case D.ChangeType.change:
                        current_length += 1
                        self.print_double(print_key_str, item.old, item.new, "Changed", output, structure_set, trace)
                    case D.ChangeType.removal:
                        removal_length += 1
                        self.print_single(print_key_str, item.old, "Removed", output, structure_set[D.DiffType.old], trace)
            else:
                current_length += 1
                if structure_set[D.DiffType.not_diff] is None:
                    if self.print_all:
                        output.extend(self.print_item(index, item, structure_set.print_text(D.DiffType.not_diff, item, trace.copy(self.name, index)), message="Unchanged "))
                    pass # This means that it is not a Diff and does not contains Diffs, so there is no text to write.
                else:
                    new_trace = trace.copy(self.name, index)
                    substructure_output, has_changes = structure_set.compare_text(D.DiffType.not_diff, item, new_trace)
                    if has_changes:
                        any_changes = True
                        if self.ordered:
                            output.append(SU.Line("Changed %s %i:") % (self.name, index))
                        else:
                            output.append(SU.Line("Changed %s:") % (self.name))
                        output.extend(line.indent() for line in substructure_output)
                    elif self.print_all:
                        output.extend(self.print_item(index, item, structure_set.print_text(D.DiffType.not_diff, item, new_trace), message="Unchanged "))
        if self.measure_length and size_changed:
            output = [SU.Line("Total %s: %i (+%i, -%i)") % (self.name, current_length, addition_length, removal_length)] + output
        return output, any_changes
