from typing import Any, Iterable, Sequence, TypeVar

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureSet as StructureSet
import Structure.StructureUtilities as SU
import Structure.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

d = TypeVar("d")

class ListStructure(Structure.Structure[Iterable[d]]):

    def __init__(
            self,
            name:str,
            field:str,
            structure:Structure.Structure[d]|None|dict[type,Structure.Structure[d]|None],
            types:tuple[type,...]|None,
            print_flat:bool,
            ordered:bool,
            measure_length:bool,
            print_all:bool,
            tags:list[str],
            normalizer:list[Normalizer.Normalizer]|None,
            children_has_normalizer:bool,
            children_tags:set[str]
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
        super().__init__(name, field, normalizer, children_has_normalizer, children_tags)

        self.structure = structure
        self.types = (object,) if types is None else types
        self.print_flat = print_flat
        self.ordered = ordered
        self.measure_length = measure_length
        self.print_all = print_all
        self.tags = tags

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", True, str),
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
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a list or None", True, TypeVerifier.UnionTypeVerifier("a list or None", TypeVerifier.UnionTypeVerifier("a list or None", type(None), TypeVerifier.ListTypeVerifier(Normalizer.Normalizer, list, "a Normalizer", "a list", additional_function=lambda data: (len(data) > 0, "empty"))))),
        TypeVerifier.TypedDictKeyTypeVerifier("children_has_normalizer", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("children_tags", "a set", True, TypeVerifier.IterableTypeVerifier(str, set, "a str", "a set")),
    )

    def check_initialization_parameters(self) -> None:
        self.type_verifier.base_verify({
            "name": self.name,
            "field": self.field,
            "structure": self.structure,
            "types": self.types,
            "print_flat": self.print_flat,
            "ordered": self.ordered,
            "measure_length": self.measure_length,
            "print_all": self.print_all,
            "tags": self.tags,
            "normalizer": self.normalizer,
            "children_has_normalizer": self.children_has_normalizer,
            "children_tags": self.children_tags,
        })

    def check_type(self, index:int, item:d) -> Trace.ErrorTrace|None:
        if isinstance(item, D.Diff):
            raise TypeError("`check_all_types` was given data containing Diffs!")
        if not isinstance(item, self.types):
            item_types_string = ", ".join(type_key.__name__ for type_key in self.types)
            return Trace.ErrorTrace(TypeError("Index, item %i: %s in %s excepted is %s instead of [%s]!" % (index, SU.stringify(item), self.name, item.__class__.__name__, item_types_string)), self.name, None, item)

    def check_all_types(self, data:list[d]) -> list[Trace.ErrorTrace]:
        '''Recursively checks if the types are correct. Should not be given data containing Diffs.'''
        output:list[Trace.ErrorTrace] = []
        for index, item in enumerate(data):
            check_type_output = self.check_type(index, item)
            if check_type_output is not None:
                output.append(check_type_output)
                continue

            structure, new_exceptions = self.choose_structure_flat(index, type(item), item)
            for exception in new_exceptions: exception.add(self.name, index)
            output.extend(new_exceptions)
            if structure is not None:
                new_exceptions = structure.check_all_types(item)
                for exception in new_exceptions: exception.add(self.name, index)
                output.extend(new_exceptions)
        return output

    def normalize(self, data:list[d], normalizer_dependencies:Normalizer.LocalNormalizerDependencies, version_number:int) -> tuple[Any|None,list[Trace.ErrorTrace]]:
        if not self.children_has_normalizer: return None, []
        if self.normalizer is not None:
            for normalizer in self.normalizer:
                try:
                    normalizer(data, normalizer_dependencies, version_number)
                except Exception as e:
                    return None, [Trace.ErrorTrace(e, self.name, None, data)]
        exceptions:list[Trace.ErrorTrace] = []
        for index, item in enumerate(data):
            structure, new_exceptions = self.choose_structure_flat(index, type(item), item)
            for exception in new_exceptions: exception.add(self.name, index)
            exceptions.extend(new_exceptions)
            if structure is not None:
                normalizer_output, new_exceptions = structure.normalize(item, normalizer_dependencies, version_number)
                for exception in new_exceptions: exception.add(self.name, index)
                exceptions.extend(new_exceptions)
                if normalizer_output is not None:
                    data[index] = normalizer_output
        return None, exceptions

    def get_tag_paths(self, data: list[d], tag: str, data_path: DataPath.DataPath) -> tuple[list[DataPath.DataPath], list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        output:list[DataPath.DataPath] = []
        exceptions:list[Trace.ErrorTrace] = []
        if tag in self.tags:
            output.extend(data_path.copy((index, type(value))).embed(value) for index, value in enumerate(data))
        for index, value in enumerate(data):
            structure, new_exceptions = self.choose_structure_flat(index, type(value), value)
            for exception in new_exceptions: exception.add(self.name, index)
            exceptions.extend(new_exceptions)
            if structure is not None:
                new_tags, new_exceptions = structure.get_tag_paths(value, tag, data_path.copy((index, type(value))))
                output.extend(new_tags)
                for exception in new_exceptions: exception.add(self.name, index)
                exceptions.extend(new_exceptions)
        return output, exceptions

    def compare(
            self,
            data1:Sequence[d],
            data2:Sequence[d],
        ) -> tuple[Sequence[d|D.Diff[d|D.NoExist,d|D.NoExist]],bool,list[Trace.ErrorTrace]]:
        if type(data1) != type(data2):
            raise TypeError("Attempted to compare type %s with type %s!" % (data1.__class__.__name__, data2.__class__.__name__))
        if data1 is data2 or data1 == data2:
            return data1, False, []
        has_changes = False
        exceptions:list[Trace.ErrorTrace] = []

        output:list[d|D.Diff[d|D.NoExist,d|D.NoExist]] = type(data1)() # type: ignore
        exceptions:list[Trace.ErrorTrace] = []
        if self.ordered:
            index = -1
            for index, (item1, item2) in enumerate(zip(data1, data2)):
                # type exception handling
                if (check_type_exception := self.check_type(index, item1)) is not None:
                    exceptions.append(check_type_exception)
                if (check_type_exception := self.check_type(index, item2)) is not None:
                    exceptions.append(check_type_exception)

                if item1 == item2:
                    output.append(item1)
                else:
                    structure_set, new_exceptions = self.choose_structure(index, D.Diff(item1, item2))
                    for exception in new_exceptions: exception.add(self.name, index)
                    exceptions.extend(new_exceptions)
                    compare_output, subcomponent_has_changes, new_exceptions = structure_set.compare(item1, item2)
                    has_changes = has_changes or subcomponent_has_changes
                    output.append(compare_output)
                    for exception in new_exceptions: exception.add(self.name, index)
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
                    if (check_type_exception := self.check_type(index + i + 1, item)) is not None:
                        exceptions.append(check_type_exception)
                    output.append((D.Diff(old=item) if data1_is_bigger else D.Diff(new=item)))
                    has_changes = True
            else: pass
            return output, has_changes, exceptions
        else: # unordered can only have additions or removals, no changes.
            for index, item in enumerate(data1):
                if (check_type_exception := self.check_type(index, item)) is not None:
                    exceptions.append(check_type_exception)
                if item in data2:
                    output.append(item) # item in both
                else:
                    output.append(D.Diff(old=item))
                    has_changes = True
            for index, item in enumerate(data2):
                if (check_type_exception := self.check_type(index, item)) is not None:
                    exceptions.append(check_type_exception)
                if item in data1:
                    pass # ignore; already added.
                else:
                    output.append(D.Diff(new=item))
                    has_changes = True
            return output, has_changes, exceptions

    def choose_structure_flat(self, key:int, value_type:type[d], value:d|None) -> tuple[Structure.Structure|None,list[Trace.ErrorTrace]]:
        if isinstance(self.structure, dict):
            output = self.structure.get(value_type, Structure.StructureFailure.choose_structure_failure)
            if output is Structure.StructureFailure.choose_structure_failure:
                return None, [Trace.ErrorTrace(KeyError("Failed to get Structure of item %i: %s" % (key, value_type)), self.name, key, value)]
            return output, []
        else:
            return self.structure, []

    def choose_structure(self, index:int, item:d|D.Diff[d,d]) -> tuple[StructureSet.StructureSet, list[Trace.ErrorTrace]]:
        output:dict[D.DiffType,Structure.Structure|None] = {}
        exceptions:list[Trace.ErrorTrace] = []
        for item_iter, diff_type in D.iter_diff(item):
            if isinstance(self.structure, dict):
                structure = self.structure.get(type(item_iter), Structure.StructureFailure.choose_structure_failure)
                if structure is Structure.StructureFailure.choose_structure_failure:
                    exceptions.append(Trace.ErrorTrace(KeyError("Failed to get Structure of item %i: %s" % (index, item_iter)), self.name, index, item))
                    continue
                output[diff_type] = structure
            else:
                output[diff_type] = self.structure
        return StructureSet.StructureSet(output), exceptions

    def print_item(self, index:int, item:d, substructure_output:list[SU.Line], message:str="") -> list[SU.Line]:
        match len(substructure_output), self.ordered:
            case 0, True:
                return [SU.Line("%s%s %i: empty") % (message, self.field, index)]
            case 0, False:
                return [SU.Line("%s%s: empty") % (message, self.field)]
            case 1, True:
                return [SU.Line("%s%s %i: %s") % (message, self.field, index, substructure_output[0])]
            case 1, False:
                return [SU.Line("%s%s: %s") % (message, self.field, substructure_output[0])]
            case _:
                output:list[SU.Line] = []
                if self.ordered:
                    output.append(SU.Line("%s%s %i:") % (message, self.field, index))
                else:
                    output.append(SU.Line("%s%s:") % (message, self.field))
                output.extend(line.indent() for line in substructure_output)
                return output

    def print_text(self, data:Iterable[d]) -> tuple[list[SU.Line],list[Trace.ErrorTrace]]:
        output:list[SU.Line] = []
        exceptions:list[Trace.ErrorTrace] = []
        items_str:list[str] = [] # print_flat only
        if not isinstance(data, Iterable):
            return [], [Trace.ErrorTrace(TypeError("`data` is not an Iterable, but instead type %s!" % (type(data))), self.name, None, data)]
        for index, item in enumerate(data):
            structure_set, new_exceptions = self.choose_structure(index, item)
            for exception in new_exceptions: exception.add(self.name, index)
            exceptions.extend(new_exceptions)

            substructure_output, new_exceptions = structure_set.print_text(D.DiffType.not_diff, item)
            for exception in new_exceptions: exception.add(self.name, index)
            exceptions.extend(new_exceptions)
            if self.print_flat:
                if len(substructure_output) == 1:
                    items_str.append(substructure_output[0].text)
                else:
                    exceptions.append(Trace.ErrorTrace(RuntimeError("Substructure of flat-printing returned multiple lines!"), self.name, index, item))
            else:
                output.extend(self.print_item(index, item, substructure_output))
        if self.print_flat:
            output.append(SU.Line("[" + ", ".join(items_str) + "]"))
        return output, exceptions

    def compare_text(self, data:Iterable[d]) -> tuple[list[SU.Line],bool, list[Trace.ErrorTrace]]:
        output:list[SU.Line] = []
        exceptions:list[Trace.ErrorTrace] = []
        any_changes = False
        if not isinstance(data, Iterable):
            return [], False, [Trace.ErrorTrace(TypeError("`data` is not an Iterable, but instead type %s!" % (type(data))), self.name, None, data)]
        current_length, addition_length, removal_length = 0, 0, 0
        size_changed = False
        for index, item in enumerate(data):
            structure_set, new_exceptions = self.choose_structure(index, item)
            for exception in new_exceptions: exception.add(self.name, index)
            exceptions.extend(new_exceptions)

            if isinstance(item, D.Diff):
                any_changes = True
                print_key_str = index if self.ordered else None
                size_changed = True
                match item.change_type:
                    case D.ChangeType.addition:
                        current_length += 1; addition_length += 1
                        new_exceptions = self.print_single(print_key_str, item.new, "Added", output, structure_set[D.DiffType.new])
                    case D.ChangeType.change:
                        current_length += 1
                        new_exceptions = self.print_double(print_key_str, item.old, item.new, "Changed", output, structure_set)
                    case D.ChangeType.removal:
                        removal_length += 1
                        new_exceptions = self.print_single(print_key_str, item.old, "Removed", output, structure_set[D.DiffType.old])
                for exception in new_exceptions: exception.add(self.name, index)
                exceptions.extend(new_exceptions)
            else:
                current_length += 1
                if structure_set[D.DiffType.not_diff] is None:
                    if self.print_all:
                        substructure_output, new_exceptions = structure_set.print_text(D.DiffType.not_diff, item)
                        for exception in new_exceptions: exception.add(self.name, index)
                        exceptions.extend(new_exceptions)
                        output.extend(self.print_item(index, item, substructure_output, message="Unchanged "))
                    pass # This means that it is not a Diff and does not contains Diffs, so there is no text to write.
                else:
                    substructure_output, has_changes, new_exceptions = structure_set.compare_text(D.DiffType.not_diff, item)
                    for exception in new_exceptions: exception.add(self.name, index)
                    exceptions.extend(new_exceptions)
                    if has_changes:
                        any_changes = True
                        if self.ordered:
                            output.append(SU.Line("Changed %s %i:") % (self.field, index))
                        else:
                            output.append(SU.Line("Changed %s:") % (self.field))
                        output.extend(line.indent() for line in substructure_output)
                    elif self.print_all:
                        substructure_output, new_exceptions = structure_set.print_text(D.DiffType.not_diff, item)
                        for exception in new_exceptions: exception.add(self.name, index)
                        exceptions.extend(new_exceptions)
                        output.extend(self.print_item(index, item, substructure_output, message="Unchanged "))
        if self.measure_length and size_changed:
            output = [SU.Line("Total %s: %i (+%i, -%i)") % (self.field, current_length, addition_length, removal_length)] + output
        return output, any_changes, exceptions
