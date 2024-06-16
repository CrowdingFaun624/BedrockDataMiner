from typing import Any, Iterable, Literal, Sequence, TypeVar

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureSet as StructureSet
import Structure.StructureUtilities as SU
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions
import Utilities.Nbt.NbtTypes as NbtTypes

d = TypeVar("d")

class ListStructure(Structure.Structure[Iterable[d]]):

    valid_types = (list, NbtTypes.TAG_List, NbtTypes.TAG_Byte_Array, NbtTypes.TAG_Int_Array, NbtTypes.TAG_Long_Array)

    def __init__(
            self,
            name:str,
            field:str,
            print_flat:bool,
            ordered:bool,
            measure_length:bool,
            print_all:bool,
            children_has_normalizer:bool,
            children_tags:set[str]
        ) -> None:
        super().__init__(name, field, children_has_normalizer, children_tags)

        self.print_flat = print_flat
        self.ordered = ordered
        self.measure_length = measure_length
        self.print_all = print_all

        self.structure:Structure.Structure[d]|dict[type,Structure.Structure[d]|None]|None = None
        self.types:tuple[type,...]|None = None
        self.normalizer:list[Normalizer.Normalizer]|None = None
        self.tags:list[str]|None = None

    def link_substructures(
        self,
        structure:Structure.Structure[d]|None|dict[type,Structure.Structure[d]|None],
        types:list[type],
        normalizer:list[Normalizer.Normalizer],
        tags:list[str],
    ) -> None:
        self.structure = structure
        self.types = tuple(types)
        self.normalizer = normalizer
        self.tags = tags

    def iter_structures(self) -> Iterable[Structure.Structure]:
        if self.structure is None: return []
        elif isinstance(self.structure, dict): return (substructure for substructure in self.structure.values() if substructure is not None)
        else: return [self.structure]

    def check_type(self, index:int, item:d) -> Trace.ErrorTrace|None:
        if self.types is None:
            raise Exceptions.AttributeNoneError("types", self)
        if not isinstance(item, self.types):
            item_types_string = ", ".join(type_key.__name__ for type_key in self.types)
            return Trace.ErrorTrace(Exceptions.StructureTypeError(self.types, type(item), "Item"), self.name, None, item)

    def check_all_types(self, data:list[d], environment:StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
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
                new_exceptions = structure.check_all_types(item, environment)
                for exception in new_exceptions: exception.add(self.name, index)
                output.extend(new_exceptions)
        return output

    def normalize(self, data:list[d], normalizer_dependencies:Normalizer.LocalNormalizerDependencies, version_number:Literal[1,2], environment:StructureEnvironment.StructureEnvironment) -> tuple[Any|None,list[Trace.ErrorTrace]]:
        if not self.children_has_normalizer: return None, []
        if self.normalizer is None:
            raise Exceptions.AttributeNoneError("normalizer", self)
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
                normalizer_output, new_exceptions = structure.normalize(item, normalizer_dependencies, version_number, environment)
                for exception in new_exceptions: exception.add(self.name, index)
                exceptions.extend(new_exceptions)
                if normalizer_output is not None:
                    data[index] = normalizer_output
        return None, exceptions

    def get_tag_paths(self, data: list[d], tag: str, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath], list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        output:list[DataPath.DataPath] = []
        exceptions:list[Trace.ErrorTrace] = []
        if self.tags is None:
            raise Exceptions.AttributeNoneError("tags", self)
        if tag in self.tags:
            output.extend(data_path.copy((index, type(value))).embed(value) for index, value in enumerate(data))
        for index, value in enumerate(data):
            structure, new_exceptions = self.choose_structure_flat(index, type(value), value)
            for exception in new_exceptions: exception.add(self.name, index)
            exceptions.extend(new_exceptions)
            if structure is not None:
                new_tags, new_exceptions = structure.get_tag_paths(value, tag, data_path.copy((index, type(value))), environment)
                output.extend(new_tags)
                for exception in new_exceptions: exception.add(self.name, index)
                exceptions.extend(new_exceptions)
        return output, exceptions

    def compare(
            self,
            data1:Sequence[d],
            data2:Sequence[d],
            environment:StructureEnvironment.StructureEnvironment,
        ) -> tuple[Sequence[d|D.Diff[d|D.NoExist,d|D.NoExist]],bool,list[Trace.ErrorTrace]]:
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
                    compare_output, subcomponent_has_changes, new_exceptions = structure_set.compare(item1, item2, environment)
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
                return None, [Trace.ErrorTrace(Exceptions.StructureTypeError(tuple(self.structure.keys()), value_type, "Item"), self.name, key, value)]
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
                    exceptions.append(Trace.ErrorTrace(Exceptions.StructureTypeError(tuple(self.structure.keys()), type(item), "Item"), self.name, index, item))
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

    def print_text(self, data:Iterable[d], environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line],list[Trace.ErrorTrace]]:
        output:list[SU.Line] = []
        exceptions:list[Trace.ErrorTrace] = []
        items_str:list[str] = [] # print_flat only
        if not isinstance(data, self.valid_types):
            return [], [Trace.ErrorTrace(Exceptions.StructureTypeError(self.valid_types, type(data), "Data"), self.name, None, data)]
        for index, item in enumerate(data):
            structure_set, new_exceptions = self.choose_structure(index, item)
            for exception in new_exceptions: exception.add(self.name, index)
            exceptions.extend(new_exceptions)

            substructure_output, new_exceptions = structure_set.print_text(D.DiffType.not_diff, item, environment)
            for exception in new_exceptions: exception.add(self.name, index)
            exceptions.extend(new_exceptions)
            if self.print_flat:
                if len(substructure_output) == 1:
                    items_str.append(substructure_output[0].text)
                else:
                    exceptions.append(Trace.ErrorTrace(Exceptions.StructureCannotPrintFlatError(), self.name, index, item))
            else:
                output.extend(self.print_item(index, item, substructure_output))
        if self.print_flat:
            output.append(SU.Line("[" + ", ".join(items_str) + "]"))
        return output, exceptions

    def compare_text(self, data:Iterable[d], environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line],bool, list[Trace.ErrorTrace]]:
        output:list[SU.Line] = []
        exceptions:list[Trace.ErrorTrace] = []
        any_changes = False
        if not isinstance(data, self.valid_types):
            return [], False, [Trace.ErrorTrace(Exceptions.StructureTypeError(self.valid_types, type(data), "Data"), self.name, None, data)]
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
                        new_exceptions = self.print_single(print_key_str, item.new, "Added", output, structure_set[D.DiffType.new], environment)
                    case D.ChangeType.change:
                        current_length += 1
                        new_exceptions = self.print_double(print_key_str, item.old, item.new, "Changed", output, structure_set, environment)
                    case D.ChangeType.removal:
                        removal_length += 1
                        new_exceptions = self.print_single(print_key_str, item.old, "Removed", output, structure_set[D.DiffType.old], environment)
                for exception in new_exceptions: exception.add(self.name, index)
                exceptions.extend(new_exceptions)
            else:
                current_length += 1
                if structure_set[D.DiffType.not_diff] is None:
                    if self.print_all:
                        substructure_output, new_exceptions = structure_set.print_text(D.DiffType.not_diff, item, environment)
                        for exception in new_exceptions: exception.add(self.name, index)
                        exceptions.extend(new_exceptions)
                        output.extend(self.print_item(index, item, substructure_output, message="Unchanged "))
                    pass # This means that it is not a Diff and does not contains Diffs, so there is no text to write.
                else:
                    substructure_output, has_changes, new_exceptions = structure_set.compare_text(D.DiffType.not_diff, item, environment)
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
                        substructure_output, new_exceptions = structure_set.print_text(D.DiffType.not_diff, item, environment)
                        for exception in new_exceptions: exception.add(self.name, index)
                        exceptions.extend(new_exceptions)
                        output.extend(self.print_item(index, item, substructure_output, message="Unchanged "))
        if self.measure_length and size_changed:
            output = [SU.Line("Total %s: %i (+%i, -%i)") % (self.field, current_length, addition_length, removal_length)] + output
        return output, any_changes, exceptions
