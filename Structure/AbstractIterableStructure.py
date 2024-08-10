from typing import Any, Iterable, TypeVar

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.ObjectStructure as ObjectStructure
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureUtilities as SU
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions
import Utilities.Nbt.NbtTypes as NbtTypes

d = TypeVar("d")

class AbstractIterableStructure(ObjectStructure.ObjectStructure[Iterable[d]]):
    """
    Abstract class of list-using Structures.
    Must override `compare`, `get_similarity`, `get_item_key`, and `get_compare_text_key_str`.
    """

    valid_types = (list, NbtTypes.TAG_List, NbtTypes.TAG_Byte_Array, NbtTypes.TAG_Int_Array, NbtTypes.TAG_Long_Array)

    def __init__(
            self,
            name:str,
            field:str,
            print_flat:bool,
            measure_length:bool,
            print_all:bool,
            children_has_normalizer:bool,
            children_tags:set[str]
        ) -> None:
        super().__init__(name, field, children_has_normalizer, children_tags)

        self.print_flat = print_flat
        self.measure_length = measure_length
        self.print_all = print_all

        self.structure:Structure.Structure[d]|None = None
        self.types:tuple[type,...]|None = None
        self.normalizer:list[Normalizer.Normalizer]|None = None
        self.post_normalizer:list[Normalizer.Normalizer]|None = None
        self.pre_normalized_types:tuple[type,...]|None = None
        self.tags:list[str]|None = None

    def link_substructures(
        self,
        structure:Structure.Structure[d]|None,
        types:tuple[type,...],
        normalizer:list[Normalizer.Normalizer],
        post_normalizer:list[Normalizer.Normalizer],
        pre_normalized_types:tuple[type,...],
        tags:list[str],
    ) -> None:
        self.structure = structure
        self.types = types
        self.normalizer = normalizer
        self.post_normalizer = post_normalizer
        self.pre_normalized_types = pre_normalized_types
        self.tags = tags

    def iter_structures(self) -> Iterable[Structure.Structure]:
        if self.structure is None: return []
        else: return [self.structure]

    def check_type(self, index:int, item:d) -> Trace.ErrorTrace|None:
        if self.types is None:
            raise Exceptions.AttributeNoneError("types", self)
        if not isinstance(item, self.types):
            return Trace.ErrorTrace(Exceptions.StructureTypeError(self.types, type(item), "Item"), self.name, index, item)

    def check_all_types(self, data:list[d], environment:StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        '''Recursively checks if the types are correct. Should not be given data containing Diffs.'''
        output:list[Trace.ErrorTrace] = []
        if not isinstance(data, self.valid_types):
            output.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.valid_types, type(data), "Data"), self.name, None, data))
            return output
        for index, item in enumerate(data):
            check_type_output = self.check_type(index, item)
            if check_type_output is not None:
                output.append(check_type_output)
                continue

            if self.structure is not None:
                output.extend(exception.add(self.name, index) for exception in self.structure.check_all_types(item, environment))
        return output

    def normalize(self, data:list[d], environment:StructureEnvironment.StructureEnvironment) -> tuple[Any|None,list[Trace.ErrorTrace]]:
        if not self.children_has_normalizer: return None, []
        if self.normalizer is None:
            raise Exceptions.AttributeNoneError("normalizer", self)
        if self.post_normalizer is None:
            raise Exceptions.AttributeNoneError("post_normalizer", self)
        if self.pre_normalized_types is None:
            raise Exceptions.AttributeNoneError("pre_normalized_types", self)
        exceptions:list[Trace.ErrorTrace] = []
        if not isinstance(data, self.pre_normalized_types):
            exceptions.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.pre_normalized_types, type(data), "Data", "(pre-normalized)"), self.name, None, data))

        data_identity_changed = False
        for normalizer in self.normalizer:
            try:
                normalizer_output = normalizer(data)
                if normalizer_output is not None:
                    data_identity_changed = True
                    data = normalizer_output
            except Exception as e:
                return None, [Trace.ErrorTrace(e, self.name, None, data)]

        for index, item in enumerate(data):
            if self.structure is not None:
                normalizer_output, new_exceptions = self.structure.normalize(item, environment)
                exceptions.extend(exception.add(self.name, index) for exception in new_exceptions)
                if normalizer_output is not None:
                    data[index] = normalizer_output

        for normalizer in self.post_normalizer:
            try:
                normalizer_output = normalizer(data)
                if normalizer_output is not None:
                    data_identity_changed = True
                    data = normalizer_output
            except Exception as e:
                return None, [Trace.ErrorTrace(e, self.name, None, data)]

        if data_identity_changed:
            return data, exceptions
        else:
            return None, exceptions

    def get_tag_paths(self, data: list[d], tag: str, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath], list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        output:list[DataPath.DataPath] = []
        exceptions:list[Trace.ErrorTrace] = []
        if self.tags is None:
            raise Exceptions.AttributeNoneError("tags", self)
        if tag in self.tags:
            output.extend(data_path.copy(index).embed(value) for index, value in enumerate(data))
        for index, value in enumerate(data):
            if self.structure is not None:
                new_tags, new_exceptions = self.structure.get_tag_paths(value, tag, data_path.copy(index), environment)
                output.extend(new_tags)
                exceptions.extend(exception.add(self.name, index) for exception in new_exceptions)
        return output, exceptions

    def get_item_key(self, index:int) -> str:
        ...

    def get_compare_text_key_str(self, index:int) -> str|int|None:
        ...

    def print_item(self, index:int, substructure_output:list[SU.Line], message:str="") -> list[SU.Line]:
        substructure_output_length = len(substructure_output)
        item_key = self.get_item_key(index)
        if substructure_output_length == 0:
            return [SU.Line("%s%s%s: empty") % (message, self.field, item_key)]
        elif substructure_output_length == 1:
            return [SU.Line("%s%s%s: %s") % (message, self.field, item_key, substructure_output[0])]
        else:
            output:list[SU.Line] = []
            output.append(SU.Line("%s%s%s:") % (message, self.field, item_key))
            output.extend(line.indent() for line in substructure_output)
            return output

    def print_text(self, data:Iterable[d], environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line],list[Trace.ErrorTrace]]:
        output:list[SU.Line] = []
        exceptions:list[Trace.ErrorTrace] = []
        items_str:list[str] = [] # print_flat only
        for index, item in enumerate(data):
            if self.structure is None:
                substructure_output = [SU.Line(SU.stringify(item))]
            else:
                substructure_output, new_exceptions = self.structure.print_text(item, environment)
                exceptions.extend(exception.add(self.name, index) for exception in new_exceptions)
            if self.print_flat:
                if len(substructure_output) == 1:
                    items_str.append(substructure_output[0].text)
                else:
                    exceptions.append(Trace.ErrorTrace(Exceptions.StructureCannotPrintFlatError(), self.name, index, item))
            else:
                output.extend(self.print_item(index, substructure_output))
        if self.print_flat:
            output.append(SU.Line("[" + ", ".join(items_str) + "]"))
        return output, exceptions

    def compare_text(self, data:Iterable[d], environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line],bool, list[Trace.ErrorTrace]]:
        output:list[SU.Line] = []
        exceptions:list[Trace.ErrorTrace] = []
        any_changes = False
        current_length, addition_length, removal_length = 0, 0, 0
        size_changed = False
        for index, item in enumerate(data):

            item_key = self.get_compare_text_key_str(index)
            if isinstance(item, D.Diff):
                any_changes = True
                size_changed = True

                match item.change_type:
                    case D.ChangeType.addition:
                        current_length += 1; addition_length += 1
                        new_exceptions = self.print_single(item_key, item.new, "Added", output, self.structure, environment)
                    case D.ChangeType.change:
                        current_length += 1
                        new_exceptions = self.print_double(item_key, item.old, item.new, "Changed", output, self.structure, environment)
                    case D.ChangeType.removal:
                        removal_length += 1
                        new_exceptions = self.print_single(item_key, item.old, "Removed", output, self.structure, environment)
                exceptions.extend(exception.add(self.name, index) for exception in new_exceptions)
            else:
                current_length += 1
                if self.structure is None:
                    if self.print_all:
                        substructure_output = [SU.Line(SU.stringify(item))]
                        output.extend(self.print_item(index, substructure_output, message="Unchanged "))
                    pass # This means that it is not a Diff and does not contains Diffs, so there is no text to write.
                else:
                    substructure_output, has_changes, new_exceptions = self.structure.compare_text(item, environment)
                    exceptions.extend(exception.add(self.name, index) for exception in new_exceptions)
                    if has_changes:
                        any_changes = True
                        output.append(SU.Line("Changed %s%s:") % (self.field, self.get_item_key(index)))
                        output.extend(line.indent() for line in substructure_output)
                    elif self.print_all:
                        substructure_output, new_exceptions = self.structure.print_text(item, environment)
                        exceptions.extend(exception.add(self.name, index) for exception in new_exceptions)
                        output.extend(self.print_item(index, substructure_output, message="Unchanged "))
        if self.measure_length and size_changed:
            output = [SU.Line("Total %s: %i (+%i, -%i)") % (self.field, current_length, addition_length, removal_length)] + output
        return output, any_changes, exceptions
