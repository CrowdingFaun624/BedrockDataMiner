from typing import Any, Generic, Hashable, Iterable, TypedDict, TypeVar, cast

from typing_extensions import NotRequired, Self

import Structure.AbstractMappingStructure as AbstractMappingStructure
import Structure.Delegate.Delegate as Delegate
import Structure.Difference as D
import Structure.ObjectStructure as ObjectStructure
import Structure.PassthroughStructure as PassthroughStructure
import Structure.PrimitiveStructure as PrimitiveStructure
import Structure.SetStructure as SetStructure
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureSet as StructureSet
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions
import Utilities.Nbt.Endianness as Endianness
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.Nbt.NbtTypes as NbtTypes
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

a = TypeVar("a", bound=Hashable)
'''
Type of the index of the iterable.
i.e., `int` for a `list`, `str` for a `dict`.
'''

b = TypeVar("b")

NoneType = type(None)

class Line():
    "A line of text in a comparison report."

    def __init__(self, text:str, *, indent:int=0) -> None:
        '''
        :text: The text to start this Line with.
        :indent: The number of indents this Line starts with.
        '''
        self.text = text
        self.indents = indent

    def set_indent(self, indents:int) -> None:
        '''
        Forcefully sets the indent of this line.
        :indents: The number of indents to set this Line to.
        '''
        self.indents = indents

    def indent(self, amount:int=1) -> Self:
        '''
        Increases the indent of this line.
        :amount: The amount to increase the indent by.
        '''
        self.indents += amount
        return self

    def __mod__(self, data:Any) -> Self:
        self.text %= data
        return self

    def __str__(self) -> str:
        return "\t" * self.indents + self.text

    def __repr__(self) -> str:
        return "<%s indent %i; len %i>" % (self.__class__.__name__, self.indents, len(self.text))

class DefaultDelegateKeysTypedDict(TypedDict):
    always_print: NotRequired[bool]

class DefaultDelegate(Delegate.Delegate[list[Line], Structure.Structure, list[tuple[Line, int]]], Generic[a]):

    applies_to = (Structure.Structure, type(None))

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str or null", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("print_flat", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("show_item_key", "a bool or null", False, (bool, type(None))),
    )

    key_type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("always_print", "a bool", False, bool),
    )

    def __init__(
        self,
        structure:ObjectStructure.ObjectStructure|None,
        keys:dict[str,DefaultDelegateKeysTypedDict],
        field:str|None=None,
        measure_length:bool=False,
        print_all:bool=False,
        print_flat:bool=False,
        show_item_key:bool|None=None,
    ) -> None:
        super().__init__(structure, keys)
        self.field = field if field is not None else ("field" if isinstance(structure, AbstractMappingStructure.AbstractMappingStructure) else "item")
        self.measure_length = measure_length
        self.print_all = print_all
        self.print_flat = print_flat
        if show_item_key is None:
            self.show_item_key = not isinstance(self.structure, SetStructure.SetStructure)
        else:
            self.show_item_key = show_item_key and not isinstance(self.structure, PassthroughStructure.PassthroughStructure)
        self.always_print_keys = cast(set[a], {key for key, value in keys.items() if value.get("always_print", False)})

    def stringify(self, data:Any) -> str:
        '''
        Returns the string of data containing no Diffs.
        :data: The data to stringify.
        '''
        match data:
            case NbtTypes.TAG():
                return str(data)
            case str():
                return "\"%s\"" % data
            case bool():
                return "true" if data else "false"
            case dict()|list()|int()|float()|bool():
                return str(data)
            case NoneType():
                return "null"
            case _:
                raise Exceptions.CannotStringifyError(type(data))

    def cache_store(self, data: list[Line], environment: StructureEnvironment.ComparisonEnvironment) -> list[tuple[Line, int]]:
        return [(line, line.indents) for line in data]

    def cache_retrieve(self, data: list[tuple[Line, int]], environment: StructureEnvironment.ComparisonEnvironment) -> list[Line]:
        output:list[Line] = []
        for line, indents in data:
            line.set_indent(indents)
            output.append(line)
        return output

    def enumerate(self, data:list[b]|dict[str,b]|set[b]) -> Iterable[tuple[a, b]]:
        '''
        Returns the key-value pairing of the data.
        For lists, calls `enumerate(data)`.
        For dicts, calls `data.items`.
        '''
        if isinstance(self.structure, AbstractMappingStructure.AbstractMappingStructure) and self.structure.sorting_function is not None and isinstance(data, dict):
            data = {key: value for key, value in sorted(data.items(), key=self.structure.sorting_function)}
        if self.structure is None or isinstance(self.structure, (PassthroughStructure.PassthroughStructure, PrimitiveStructure.PrimitiveStructure)):
            return ((None, data),) # type: ignore
        match data:
            case list() | NbtTypes.TAG_List() | NbtTypes.TAG_Int_Array() | NbtTypes.TAG_Byte_Array() | NbtTypes.TAG_Long_Array():
                return enumerate(data) # type: ignore
            case dict() | NbtTypes.TAG_Compound():
                return data.items() # type: ignore
            case set():
                return enumerate(data) # type: ignore
            case _:
                raise Exceptions.StructureTypeError((list, dict, set), type(data), "Data", "(data type not supported)")

    def get_item_key(self, index:a) -> str:
        return " " + self.stringify(index) if self.show_item_key else ""

    def get_compare_text_key_str(self, index:a) -> a|None:
        return index if self.show_item_key else None

    def print_item(self, index:a, substructure_output:list[Line], message:str="") -> list[Line]:
        substructure_output_length = len(substructure_output)
        item_key = self.get_item_key(index)
        if substructure_output_length == 0:
            return [Line("%s%s%s: empty") % (message, self.field, item_key)]
        elif substructure_output_length == 1:
            return [Line("%s%s%s: %s") % (message, self.field, item_key, substructure_output[0])]
        else:
            output:list[Line] = []
            output.append(Line("%s%s%s:") % (message, self.field, item_key))
            output.extend(line.indent() for line in substructure_output)
            return output

    def print_text(self, data:list[Any]|dict[str,Any], environment:StructureEnvironment.PrinterEnvironment) -> tuple[list[Line],list[Trace.ErrorTrace]]:
        if self.structure is None or isinstance(self.structure, (PassthroughStructure.PassthroughStructure, PrimitiveStructure.PrimitiveStructure)):
            return [Line(self.stringify(data))], []
        exceptions:list[Trace.ErrorTrace] = []
        output:list[Line] = []
        items_str:list[str] = [] # print_flat only
        for index, item in self.enumerate(data):
            if not isinstance(self.structure, ObjectStructure.ObjectStructure):
                structure = None
            else:
                structure, new_exceptions = self.structure.get_structure(index, item)
                exceptions.extend(exception.add(self.get_structure().name, index) for exception in new_exceptions)
            if structure is None:
                substructure_output = [Line(self.stringify(item))]
            else:
                substructure_output, new_exceptions = structure.print_text(item, environment)
                exceptions.extend(exception.add(self.get_structure().name, index) for exception in new_exceptions)
            if self.print_flat:
                if len(substructure_output) == 1:
                    items_str.append(substructure_output[0].text)
                else:
                    exceptions.append(Trace.ErrorTrace(Exceptions.StructureCannotPrintFlatError(), self.get_structure().name, index, item))
            else:
                output.extend(self.print_item(index, substructure_output))
        if self.print_flat:
            output.append(Line("[" + ", ".join(items_str) + "]"))
        return output, exceptions

    def compare_text(self, data:list[Any]|dict[str,Any], environment:StructureEnvironment.ComparisonEnvironment) -> tuple[list[Line],bool, list[Trace.ErrorTrace]]:
        output:list[Line] = []
        exceptions:list[Trace.ErrorTrace] = []
        any_changes = False
        current_length, addition_length, removal_length = 0, 0, 0
        size_changed = False
        for index, item in self.enumerate(data):
            can_print_print_all = True # if the print_all thing is overridden for whatever reason.
            if not isinstance(self.structure, ObjectStructure.ObjectStructure):
                structure_set = StructureSet.StructureSet({D.DiffType.old: None, D.DiffType.new: None} if isinstance(item, D.Diff) else {D.DiffType.not_diff: None})
            else:
                structure_set, new_exceptions = self.structure.choose_structure(index, item)
                exceptions.extend(exception.add(self.get_structure().name, index) for exception in new_exceptions)

            old_index:a; new_index:a
            if isinstance(index, D.Diff):
                index_diff = cast(D.Diff[a,a], index)
                old_index, new_index = index_diff.old, index_diff.new
                if index_diff.is_change:
                    can_print_print_all = False
                    any_changes = True
                    output.append(Line("Moved %s %s to %s.") % (self.field, self.stringify(index.old), self.stringify(index.new)))
            else:
                old_index, new_index = index, index

            if isinstance(item, D.Diff):
                any_changes = True
                size_changed = True

                match item.change_type:
                    case D.ChangeType.addition:
                        item_key = self.get_compare_text_key_str(new_index)
                        current_length += 1; addition_length += 1
                        new_exceptions = self.print_single(item_key, item.new, "Added", output, structure_set[D.DiffType.new], environment[1])
                    case D.ChangeType.change:
                        item_key = self.get_compare_text_key_str(new_index)
                        current_length += 1
                        new_exceptions = self.print_double(item_key, item.old, item.new, "Changed", output, structure_set, environment)
                    case D.ChangeType.removal:
                        item_key = self.get_compare_text_key_str(old_index)
                        removal_length += 1
                        new_exceptions = self.print_single(item_key, item.old, "Removed", output, structure_set[D.DiffType.old], environment[0])
                exceptions.extend(exception.add(self.get_structure().name, new_index) for exception in new_exceptions)
            else:
                substructure_output:list[Line]
                current_length += 1
                structure = structure_set[D.DiffType.not_diff]
                if structure is None:
                    if (self.print_all or new_index in self.always_print_keys) and can_print_print_all:
                        substructure_output = [Line(self.stringify(item))]
                        output.extend(self.print_item(new_index, substructure_output, message="Unchanged "))
                    pass # This means that it is not a Diff and does not contains Diffs, so there is no text to write.
                else:
                    substructure_output, has_changes, new_exceptions = structure.compare_text(item, environment)
                    exceptions.extend(exception.add(self.get_structure().name, new_index) for exception in new_exceptions)
                    if has_changes:
                        any_changes = True
                        output.append(Line("Changed %s%s:") % (self.field, self.get_item_key(new_index)))
                        output.extend(line.indent() for line in substructure_output)
                    elif (self.print_all or new_index in self.always_print_keys) and can_print_print_all:
                        substructure_output, new_exceptions = structure.print_text(item, environment[1])
                        exceptions.extend(exception.add(self.get_structure().name, new_index) for exception in new_exceptions)
                        output.extend(self.print_item(new_index, substructure_output, message="Unchanged "))
        if self.measure_length and size_changed:
            output = [Line("Total %s: %i (+%i, -%i)") % (self.field, current_length, addition_length, removal_length)] + output
        return output, any_changes, exceptions

    def print_single(self, key_str:a|None, data:Any, message:str, output:list[Line], printer:Structure.Structure|None, environment:StructureEnvironment.PrinterEnvironment, *, post_message:str="") -> list[Trace.ErrorTrace]:
        '''
        Adds text from a single-type Diff (i.e. an addition or removal). Returns a list of ErrorTraces.
        :key_str: The key to describe the data with. If None, it will not be present.
        :data: The data to print (containing no Diffs).
        :message: The capitalized string describing what happened to the data (i.e. "Added" or "Removed").
        :output: The list of Lines to output to.
        :printer: The Structure (or None) to print the data with.
        :environment: The StructureEnvironment to use.
        :post_message: A string to put after the field.
        '''
        exceptions:list[Trace.ErrorTrace] = []
        if printer is None:
            stringified_data = self.stringify(data)
            if key_str is None:
                output.append(Line("%s %s%s %s.") % (message, self.field, post_message, stringified_data))
            else:
                output.append(Line("%s %s%s %s of %s.") % (message, self.field, post_message, self.stringify(key_str), stringified_data))
        else:
            substructure_output, new_exceptions = printer.print_text(data, environment)
            exceptions.extend(exception.add(self.get_structure().name, key_str) for exception in new_exceptions)
            match len(substructure_output), key_str is None:
                case 0, True:
                    output.append(Line("%s empty %s%s.") % (message, self.field, post_message))
                case 0, False:
                    output.append(Line("%s empty %s%s %s.") % (message, self.field, post_message, self.stringify(key_str)))
                case 1, True:
                    output.append(Line("%s %s%s %s.") % (message, self.field, post_message, substructure_output[0]))
                case 1, False:
                    output.append(Line("%s %s%s %s of %s.") % (message, self.field, post_message, self.stringify(key_str), substructure_output[0]))
                case _, True:
                    output.append(Line("%s %s%s:") % (message, self.field, post_message))
                    output.extend(line.indent() for line in substructure_output)
                case _, False:
                    output.append(Line("%s %s%s %s:") % (message, self.field, post_message, self.stringify(key_str)))
                    output.extend(line.indent() for line in substructure_output)
        return exceptions

    def print_double(
        self,
        key_str:a|None,
        data1:Any,
        data2:Any,
        message:str,
        output:list[Line],
        printers:StructureSet.StructureSet,
        environment:StructureEnvironment.ComparisonEnvironment,
        *,
        post_message:str=""
    ) -> list[Trace.ErrorTrace]:
        '''
        Adds text from a double-type Diff (i.e. a change). Returns a list of ErrorTraces.
        :key_str: The key to describe the data with. If None, it will not be present.
        :data1: The data from the oldest Version to print (containing no Diffs).
        :data2: The data from the newest Version to print (containing no Diffs).
        :message: The capitalized string describing what happened to the data (i.e. "Added" or "Removed").
        :output: The list of Lines to output to.
        :printer: The StructureSet to print the data with.
        :environment: The ComparisonEnvironment to use.
        :post_message: A string to put after the field.
        '''
        printer1 = printers[D.DiffType.old]
        printer2 = printers[D.DiffType.new]
        exceptions:list[Trace.ErrorTrace] = []
        if printer1 is None:
            substructure_output1 = [Line(self.stringify(data1))]
        else:
            substructure_output1, new_exceptions = printer1.print_text(data1, environment[0])
            exceptions.extend(exception.add(self.get_structure().name, key_str) for exception in new_exceptions)
        if printer2 is None:
            substructure_output2 = [Line(self.stringify(data2))]
        else:
            substructure_output2, new_exceptions = printer2.print_text(data2, environment[1])
            exceptions.extend(exception.add(self.get_structure().name, key_str) for exception in new_exceptions)
        if len(substructure_output1) == 0: substructure_output1 = [Line("empty")]
        if len(substructure_output2) == 0: substructure_output2 = [Line("empty")]
        match len(substructure_output1), len(substructure_output2), key_str is None:
            case 1, 1, True:
                output.append(Line("%s %s%s from %s to %s.") % (message, self.field, post_message, substructure_output1[0], substructure_output2[0]))
            case 1, 1, False:
                output.append(Line("%s %s%s %s from %s to %s.") % (message, self.field, post_message, self.stringify(key_str), substructure_output1[0], substructure_output2[0]))
            case 1, _, True:
                output.append(Line("%s %s%s from %s to:") % (message, self.field, post_message, substructure_output1[0]))
                output.extend(line.indent() for line in substructure_output2)
            case 1, _, False:
                output.append(Line("%s %s%s %s from %s to:") % (message, self.field, post_message, self.stringify(key_str), substructure_output1[0]))
                output.extend(line.indent() for line in substructure_output2)
            case _, 1, True:
                output.append(Line("%s %s%s to %s from:") % (message, self.field, post_message, substructure_output2[0]))
                output.extend(line.indent() for line in substructure_output1)
            case _, 1, False:
                output.append(Line("%s %s%s %s to %s from:") % (message, self.field, post_message, self.stringify(key_str), substructure_output2[0]))
                output.extend(line.indent() for line in substructure_output1)
            case _, _, True:
                output.append(Line("%s %s%s from:") % (message, self.field, post_message))
                output.extend(line.indent() for line in substructure_output1)
                output.append(Line("to:"))
                output.extend(line.indent() for line in substructure_output2)
            case _, _, False:
                output.append(Line("%s %s%s %s from:") % (message, self.field, post_message, self.stringify(key_str)))
                output.extend(line.indent() for line in substructure_output1)
                output.append(Line("to:"))
                output.extend(line.indent() for line in substructure_output2)
        return exceptions
