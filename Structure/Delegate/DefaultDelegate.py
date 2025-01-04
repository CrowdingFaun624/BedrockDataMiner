from typing import Any, Hashable, Iterable, NotRequired, TypedDict, cast

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
import Utilities.TypeVerifier as TypeVerifier

NoneType = type(None)

type LineType = tuple[int,str]

class DefaultDelegateKeysTypedDict(TypedDict):
    always_print: NotRequired[bool]

class DefaultDelegate[a:Hashable](Delegate.Delegate[list[LineType], Structure.Structure, list[LineType]]):

    # NOTE: This class assumes that all diffs are of length 2

    applies_to = (Structure.Structure, type(None))

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("enquote_strings", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str or null", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("passthrough", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("print_flat", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("show_item_key", "a bool or null", False, (bool, type(None))),
    )

    key_type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("always_print", "a bool", False, bool),
    )

    __slots__ = (
        "always_print_keys",
        "enquote_strings",
        "field",
        "measure_length",
        "passthrough",
        "print_all",
        "print_flat",
        "show_item_key",
    )

    def __init__(
        self,
        structure:ObjectStructure.ObjectStructure|None,
        keys:dict[str,DefaultDelegateKeysTypedDict],
        field:str|None=None,
        measure_length:bool=False,
        passthrough:bool=False,
        print_all:bool=False,
        print_flat:bool=False,
        show_item_key:bool|None=None,
        enquote_strings:bool=True
    ) -> None:
        super().__init__(structure, keys)
        self.field = field if field is not None else ("field" if isinstance(structure, AbstractMappingStructure.AbstractMappingStructure) else "item")
        self.measure_length = measure_length
        self.passthrough = passthrough
        self.print_all = print_all
        self.print_flat = print_flat
        self.enquote_strings = enquote_strings
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
        if hasattr(data, "__stringify__"):
            return data.__stringify__()
        match data:
            case str():
                if self.enquote_strings:
                    return f"\"{data}\""
                else:
                    return data
            case bool():
                return "true" if data else "false"
            case dict()|list()|int()|float()|bool():
                return str(data)
            case NoneType():
                return "null"
            case _:
                return str(data)

    def enumerate[b](self, data:list[b]|dict[str,b]|set[b]) -> Iterable[tuple[a, b]]:
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
            case list():
                return enumerate(data) # type: ignore
            case dict():
                return data.items() # type: ignore
            case set():
                return enumerate(data) # type: ignore
            case _:
                raise Exceptions.StructureTypeError((list, dict, set), type(data), "Data", "(data type not supported)")

    def get_item_key(self, index:a) -> str:
        return " " + self.stringify(index) if self.show_item_key else ""

    def get_compare_text_key_str(self, index:a) -> a|None:
        return index if self.show_item_key else None

    def print_item(self, index:a, substructure_output:list[LineType], message:str="") -> list[LineType]:
        if self.passthrough:
            return substructure_output
        substructure_output_length = len(substructure_output)
        item_key = self.get_item_key(index)
        if substructure_output_length == 0:
            return [(0, f"{message}{self.field}{item_key}: empty")]
        elif substructure_output_length == 1:
            return [(0, f"{message}{self.field}{item_key}: {substructure_output[0][1]}")]
        else:
            output:list[LineType] = []
            output.append((0, f"{message}{self.field}{item_key}:"))
            output.extend((indentation + 1, line) for indentation, line in substructure_output)
            return output

    def print_text(self, data:list[Any]|dict[str,Any], environment:StructureEnvironment.PrinterEnvironment) -> tuple[list[LineType],list[Trace.ErrorTrace]]:
        if self.structure is None or isinstance(self.structure, (PassthroughStructure.PassthroughStructure, PrimitiveStructure.PrimitiveStructure)):
            return [(0, self.stringify(data))], []
        exceptions:list[Trace.ErrorTrace] = []
        output:list[LineType] = []
        items_str:list[str] = [] # print_flat only
        for index, item in self.enumerate(data):
            if not isinstance(self.structure, ObjectStructure.ObjectStructure):
                structure = None
            else:
                structure, new_exceptions = self.structure.get_structure(index, item)
                exceptions.extend(exception.add(self.get_structure().name, index) for exception in new_exceptions)
            if structure is None:
                substructure_output = [(0, self.stringify(item))]
            else:
                substructure_output, new_exceptions = structure.print_text(item, environment)
                exceptions.extend(exception.add(self.get_structure().name, index) for exception in new_exceptions)
            if self.print_flat:
                if len(substructure_output) == 1:
                    items_str.append(substructure_output[0][1])
                else:
                    exceptions.append(Trace.ErrorTrace(Exceptions.StructureCannotPrintFlatError(), self.get_structure().name, index, item))
            else:
                output.extend(self.print_item(index, substructure_output))
        if self.print_flat:
            output.append((0, "[" + ", ".join(items_str) + "]"))
        return output, exceptions

    def compare_text(self, data:list[Any]|dict[str,Any], environment:StructureEnvironment.ComparisonEnvironment) -> tuple[list[LineType],bool, list[Trace.ErrorTrace]]:
        output:list[LineType] = []
        exceptions:list[Trace.ErrorTrace] = []
        any_changes = False
        current_length, addition_length, removal_length = 0, 0, 0
        size_changed = False
        for index, item in self.enumerate(data):
            can_print_print_all = True # if the print_all thing is overridden for whatever reason.
            if not isinstance(self.structure, ObjectStructure.ObjectStructure):
                structure_set = StructureSet.StructureSet({(0,): None, (1,): None} if isinstance(item, D.Diff) else {None: None})
            else:
                structure_set, new_exceptions = self.structure.choose_structure(index, item)
                exceptions.extend(exception.add(self.get_structure().name, index) for exception in new_exceptions)

            old_index:a; new_index:a
            if isinstance(index, D.Diff):
                index_diff = cast("D.Diff[a]", index)
                old_index_diff, new_index_diff = index_diff.get(0), index_diff.get(1)
                old_index = old_index_diff if not isinstance(old_index_diff, D._NoExistType) else cast(a, new_index_diff)
                new_index = new_index_diff if not isinstance(new_index_diff, D._NoExistType) else old_index
                if old_index_diff is not D.NoExist and new_index_diff is not D.NoExist:
                    can_print_print_all = False
                    any_changes = True
                    output.append((0, f"Moved {self.field} {self.stringify(index_diff[0])} to {self.stringify(index_diff[1])}."))
            else:
                old_index, new_index = index, index

            if isinstance(item, D.Diff):
                any_changes = True
                size_changed = True

                match (0 in item, 1 in item):
                    case False, False:
                        raise Exceptions.DiffExistenceError(item)
                    case False, True:
                        item_key = self.get_compare_text_key_str(new_index)
                        current_length += 1; addition_length += 1
                        new_exceptions = self.print_single(item_key, item[1], "Added", output, structure_set[1], environment[1])
                    case True, False:
                        item_key = self.get_compare_text_key_str(old_index)
                        removal_length += 1
                        new_exceptions = self.print_single(item_key, item[0], "Removed", output, structure_set[0], environment[0])
                    case True, True:
                        item_key = self.get_compare_text_key_str(new_index)
                        current_length += 1
                        new_exceptions = self.print_double(item_key, item[0], item[1], "Changed", output, structure_set, environment)
                exceptions.extend(exception.add(self.get_structure().name, new_index) for exception in new_exceptions)
            else:
                substructure_output:list[LineType]
                current_length += 1
                structure = structure_set[None]
                if structure is None:
                    if (self.print_all or new_index in self.always_print_keys) and can_print_print_all:
                        substructure_output = [(0, self.stringify(item))]
                        output.extend(self.print_item(new_index, substructure_output, message="Unchanged "))
                    pass # This means that it is not a Diff and does not contains Diffs, so there is no text to write.
                else:
                    substructure_output, has_changes, new_exceptions = structure.compare_text(item, environment)
                    exceptions.extend(exception.add(self.get_structure().name, new_index) for exception in new_exceptions)
                    if has_changes:
                        any_changes = True
                        if self.passthrough:
                            output.extend(substructure_output)
                        else:
                            output.append((0, f"Changed {self.field}{self.get_item_key(new_index)}:"))
                            output.extend((indentation + 1, line) for indentation, line in substructure_output)
                    elif (self.print_all or new_index in self.always_print_keys) and can_print_print_all:
                        substructure_output, new_exceptions = structure.print_text(item, environment[1])
                        exceptions.extend(exception.add(self.get_structure().name, new_index) for exception in new_exceptions)
                        output.extend(self.print_item(new_index, substructure_output, message="Unchanged "))
        if self.measure_length and size_changed:
            output = [(0, f"Total {self.field}: {current_length} (+{addition_length}, -{removal_length})")] + output
        return output, any_changes, exceptions

    def print_single(self, key_str:a|None, data:Any, message:str, output:list[LineType], printer:Structure.Structure|None, environment:StructureEnvironment.PrinterEnvironment, *, post_message:str="") -> list[Trace.ErrorTrace]:
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
                output.append((0, f"{message} {self.field}{post_message} {stringified_data}."))
            else:
                output.append((0, f"{message} {self.field}{post_message} {self.stringify(key_str)} of {stringified_data}."))
        else:
            substructure_output:list[LineType]
            substructure_output, new_exceptions = printer.print_text(data, environment)
            exceptions.extend(exception.add(self.get_structure().name, key_str) for exception in new_exceptions)
            if self.passthrough:
                output.extend(substructure_output)
                return exceptions
            match len(substructure_output), key_str is None:
                case 0, True:
                    output.append((0, f"{message} empty {self.field}{post_message}."))
                case 0, False:
                    output.append((0, f"{message} empty {self.field}{post_message} {self.stringify(key_str)}."))
                case 1, True:
                    output.append((0, f"{message} {self.field}{post_message} {substructure_output[0][1]}."))
                case 1, False:
                    output.append((0, f"{message} {self.field}{post_message} {self.stringify(key_str)} of {substructure_output[0][1]}."))
                case _, True:
                    output.append((0, f"{message} {self.field}{post_message}:"))
                    output.extend((indentation + 1, line) for indentation, line in substructure_output)
                case _, False:
                    output.append((0, f"{message} {self.field}{post_message} {self.stringify(key_str)}:"))
                    output.extend((indentation + 1, line) for indentation, line in substructure_output)
        return exceptions

    def print_double(
        self,
        key_str:a|None,
        data1:Any,
        data2:Any,
        message:str,
        output:list[LineType],
        printers:StructureSet.StructureSet[a],
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
        printer1 = printers[0]
        printer2 = printers[1]
        exceptions:list[Trace.ErrorTrace] = []
        substructure_output1:list[LineType]
        substructure_output2:list[LineType]
        if printer1 is None:
            substructure_output1 = [(0, self.stringify(data1))]
        else:
            substructure_output1, new_exceptions = printer1.print_text(data1, environment[0])
            exceptions.extend(exception.add(self.get_structure().name, key_str) for exception in new_exceptions)
        if printer2 is None:
            substructure_output2 = [(0, self.stringify(data2))]
        else:
            substructure_output2, new_exceptions = printer2.print_text(data2, environment[1])
            exceptions.extend(exception.add(self.get_structure().name, key_str) for exception in new_exceptions)
        if self.passthrough:
            output.extend(substructure_output1)
            output.extend(substructure_output2)
            return exceptions
        if len(substructure_output1) == 0: substructure_output1 = [(0, "empty")]
        if len(substructure_output2) == 0: substructure_output2 = [(0, "empty")]
        match len(substructure_output1), len(substructure_output2), key_str is None:
            case 1, 1, True:
                output.append((0, f"{message} {self.field}{post_message} from {substructure_output1[0][1]} to {substructure_output2[0][1]}."))
            case 1, 1, False:
                output.append((0, f"{message} {self.field}{post_message} {self.stringify(key_str)} from {substructure_output1[0][1]} to {substructure_output2[0][1]}."))
            case 1, _, True:
                output.append((0, f"{message} {self.field}{post_message} from {substructure_output1[0][1]} to:"))
                output.extend((indentation + 1, line) for indentation, line in substructure_output2)
            case 1, _, False:
                output.append((0, f"{message} {self.field}{post_message} {self.stringify(key_str)} from {substructure_output1[0][1]} to:"))
                output.extend((indentation + 1, line) for indentation, line in substructure_output2)
            case _, 1, True:
                output.append((0, f"{message} {self.field}{post_message} to {substructure_output2[0][1]} from:"))
                output.extend((indentation + 1, line) for indentation, line in substructure_output1)
            case _, 1, False:
                output.append((0, f"{message} {self.field}{post_message} {self.stringify(key_str)} to {substructure_output2[0][1]} from:"))
                output.extend((indentation + 1, line) for indentation, line in substructure_output1)
            case _, _, True:
                output.append((0, f"{message} {self.field}{post_message} from:"))
                output.extend((indentation + 1, line) for indentation, line in substructure_output1)
                output.append((0, "to:"))
                output.extend((indentation + 1, line) for indentation, line in substructure_output2)
            case _, _, False:
                output.append((0, f"{message} {self.field}{post_message} {self.stringify(key_str)} from:"))
                output.extend((indentation + 1, line) for indentation, line in substructure_output1)
                output.append((0, "to:"))
                output.extend((indentation + 1, line) for indentation, line in substructure_output2)
        return exceptions
