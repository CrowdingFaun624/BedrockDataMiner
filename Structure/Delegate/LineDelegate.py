from types import EllipsisType, NoneType
from typing import Any, Sequence

import Structure.Container as Con
import Structure.Delegate.Delegate as Delegate
import Structure.Difference as Diff
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

type LineType = tuple[int,str]

class LineDelegate[DC:Con.Con, DD:Con.Don|Diff.Diff, S:Structure.Structure|None](Delegate.Delegate[DC, DD, S, list[LineType], list[LineType], list[LineType], list[LineType]]):

    __slots__ = (
        "enquote_strings",
        "field",
        "passthrough",
    )

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("enquote_strings", False, bool),
    )

    def __init__(self, structure: S, keys: dict[str, Any], field:str, enquote_strings:bool=True, passthrough:bool=False) -> NoneType:
        super().__init__(structure, keys)
        self.enquote_strings = enquote_strings
        self.field = field
        self.passthrough = passthrough

    def get_item_output[A](
        self,
        item:Con.Con[A]|EllipsisType,
        structure:Structure.Structure[A, Con.Con[A], Con.Don[A], Con.Don[A]|Diff.Diff[Con.Don[A]], list[LineType], list[LineType]]|None,
        trace:Trace.Trace,
        environment:StructureEnvironment.PrinterEnvironment,
    ) -> list[LineType]:
        if item is ...:
            return []
        elif structure is None:
            return [(0, self.stringify(item.data))]
        elif (output := structure.print_branch(item, trace, environment)) is ...:
            return []
        else:
            return output

    def stringify(self, data:Any) -> str:
        '''
        Returns the string of data containing no Diffs.
        :data: The data to stringify.
        '''
        if hasattr(data, "__stringify__"):
            return data.__stringify__() # type: ignore
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

    def print_single(self, key_output:list[LineType]|None, value_output:list[LineType], output:list[LineType], *, message:str="", post_message:str="", allow_single_line:bool=True, add_punctuation:bool=True) -> None:
        '''
        Adds text from a single-type Diff (i.e. an addition or removal).
        '''
        if self.passthrough:
            # ignore key_output
            output.extend(value_output)
        elif key_output is None and len(value_output) == 0:
            output.append((0, f"{message}empty {self.field}{post_message}{"." if add_punctuation else ""}"))
        elif key_output is None and len(value_output) == 1 and allow_single_line:
            output.append((0, f"{message}{self.field}{post_message} {value_output[0][1]}{"." if add_punctuation else ""}"))
        elif key_output is None and (len(value_output) > 1 or not allow_single_line):
            output.append((0, f"{message}{self.field}{post_message}:"))
            output.extend((indentation + 1, line) for indentation, line in value_output)
        elif key_output is not None and len(key_output) == 0 and len(value_output) == 0:
            output.append((0, f"{message}{self.field}{post_message} empty: empty{"." if add_punctuation else ""}"))
        elif key_output is not None and len(key_output) == 0 and len(value_output) == 1 and allow_single_line:
            output.append((0, f"{message}{self.field}{post_message} empty: {value_output[0][1]}{"." if add_punctuation else ""}"))
        elif key_output is not None and len(key_output) == 0 and (len(value_output) > 1 or not allow_single_line):
            output.append((0, f"{message}{self.field}{post_message} empty:"))
            output.extend((indentation + 1, line) for indentation, line in value_output)
        elif key_output is not None and len(key_output) == 1 and len(value_output) == 0:
            output.append((0, f"{message}{self.field}{post_message} {key_output[0][1]}: empty{"." if add_punctuation else ""}"))
        elif key_output is not None and len(key_output) == 1 and len(value_output) == 1 and allow_single_line:
            output.append((0, f"{message}{self.field}{post_message} {key_output[0][1]}: {value_output[0][1]}{"." if add_punctuation else ""}"))
        elif key_output is not None and len(key_output) == 1 and (len(value_output) > 1 or not allow_single_line):
            output.append((0, f"{message}{self.field}{post_message} {key_output[0][1]}:"))
            output.extend((indentation + 1, line) for indentation, line in value_output)
        elif key_output is not None and len(key_output) > 1 and len(value_output) == 0:
            output.append((0, f"{message}{self.field}{post_message}:"))
            output.extend((indentation + 1, line) for indentation, line in key_output)
            output.append((0, f"of empty{"." if add_punctuation else ""}"))
        elif key_output is not None and len(key_output) > 1 and len(value_output) == 1 and allow_single_line:
            output.append((0, f"{message}{self.field}{post_message}:"))
            output.extend((indentation + 1, line) for indentation, line in key_output)
            output.append((0, f"of {value_output[0][1]}"))
        elif key_output is not None and len(key_output) > 1 and (len(value_output) > 1 or not allow_single_line):
            output.append((0, f"{message}{self.field}{post_message}:"))
            output.extend((indentation + 1, line) for indentation, line in key_output)
            output.append((0, "of:"))
            output.extend((indentation + 1, line) for indentation, line in value_output)

    def print_double(
        self,
        key_output:Sequence[LineType]|None, # most recent
        value_output1:Sequence[LineType],
        value_output2:Sequence[LineType],
        message:str,
        output:list[LineType],
        *,
        post_message:str=""
    ) -> None:
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
        if self.passthrough:
            output.extend(value_output1)
            output.extend(value_output2)
        if key_output is None:
            key_output = []
        elif len(key_output) == 0:
            key_output = ((0, "empty"),)
        if len(value_output1) == 0:
            value_output1 = ((0, "empty"),)
        if len(value_output2) == 0:
            value_output2 = ((0, "empty"),)
        match 0 if key_output is None else len(key_output), len(value_output1), len(value_output2):
            case 0, 1, 1:
                output.append((0, f"{message}{self.field}{post_message} from {value_output1[0][1]} to {value_output2[0][1]}."))
            case 0, 1, _:
                output.append((0, f"{message}{self.field}{post_message} from {value_output1[0][1]} to:"))
                output.extend((indentation + 1, line) for indentation, line in value_output2)
            case 0, _, 1:
                output.append((0, f"{message}{self.field}{post_message} to {value_output2[0][1]} from:"))
                output.extend((indentation + 1, line) for indentation, line in value_output1)
            case 0, _, _:
                output.append((0, f"{message}{self.field}{post_message} from:"))
                output.extend((indentation + 1, line) for indentation, line in value_output1)
                output.append((0, "to:"))
                output.extend((indentation + 1, line) for indentation, line in value_output2)
            case 1, 1, 1:
                output.append((0, f"{message}{self.field}{post_message} {key_output[0][1]} from {value_output1[0][1]} to {value_output2[0][1]}."))
            case 1, 1, _:
                output.append((0, f"{message}{self.field}{post_message} {key_output[0][1]} from {value_output1[0][1]} to:"))
                output.extend((indentation + 1, line) for indentation, line in value_output2)
            case 1, _, 1:
                output.append((0, f"{message}{self.field}{post_message} {key_output[0][1]} to {value_output2[0][1]} from:"))
                output.extend((indentation + 1, line) for indentation, line in value_output1)
            case 1, _, _:
                output.append((0, f"{message}{self.field}{post_message} {key_output[0][1]} from:"))
                output.extend((indentation + 1, line) for indentation, line in value_output1)
                output.append((0, "to:"))
                output.extend((indentation + 1, line) for indentation, line in value_output2)
            case _, 1, 1:
                output.append((0, f"{message}{self.field}{post_message}:"))
                output.extend((indentation + 1, line) for indentation, line in key_output)
                output.append((0, f"from {value_output1[0][1]} to {value_output2[0][1]}."))
            case _, 1, _:
                output.append((0, f"{message}{self.field}{post_message}:"))
                output.extend((indentation + 1, line) for indentation, line in key_output)
                output.append((0, f"from {value_output1[0][1]} to:"))
                output.extend((indentation + 1, line) for indentation, line in value_output2)
            case _, _, 1:
                output.append((0, f"{message}{self.field}{post_message}:"))
                output.extend((indentation + 1, line) for indentation, line in key_output)
                output.append((0, f"to {value_output2[0][1]} from:"))
                output.extend((indentation + 1, line) for indentation, line in value_output1)
            case _, _, _:
                output.append((0, f"{message}{self.field}{post_message}:"))
                output.extend((indentation + 1, line) for indentation, line in key_output)
                output.append((0, "from:"))
                output.extend((indentation + 1, line) for indentation, line in value_output1)
                output.append((0, "to:"))
                output.extend((indentation + 1, line) for indentation, line in value_output2)
