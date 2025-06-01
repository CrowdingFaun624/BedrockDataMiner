import math
from types import EllipsisType
from typing import Sequence

import Structure.Container as Con
import Structure.Delegate.DefaultDelegate as DefaultDelegate
import Structure.Delegate.LineDelegate as LineDelegate
import Structure.Difference as Diff
import Structure.IterableContainer as ICon
import Structure.IterableStructure as IterableStructure
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Trace as Trace


class LongStringDelegate(DefaultDelegate.DefaultDelegate[int, str, Sequence]):

    __slots__ = (
        "surrounding_line_count",
    )

    def __init__(
        self,
        structure:IterableStructure.IterableStructure,
        keys:dict[str,DefaultDelegate.DefaultDelegateKeysTypedDict],
        measure_length:bool=False,
        surrounding_line_count:int|None=5,
    ) -> None:
        super().__init__(structure, keys, "line", measure_length, False, False, False, True)

        self.surrounding_line_count = surrounding_line_count

    def print_branch(self, data: ICon.ICon[Con.Con[int], Con.Con[str], Sequence], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> list[LineDelegate.LineType] | EllipsisType:
        data_list = list(data.items())
        if len(data_list) == 0:
            return [(0, "empty")]
        else:
            output:list[LineDelegate.LineType] = []
            output.append((0, "'''"))
            for index, line in data_list:
                with trace.enter_key(index, line):
                    output.append((0, line.data))
            output.append((0, "'''"))
            return output

    def get_before_buffer(self, lines_before_buffer:list[tuple[int,LineDelegate.LineType]]) -> tuple[int|None, list[LineDelegate.LineType]]:
        if self.surrounding_line_count is None:
            output = lines_before_buffer[:]
        elif len(lines_before_buffer) < self.surrounding_line_count:
            output = lines_before_buffer[:]
        else:
            output = lines_before_buffer[-self.surrounding_line_count:]
        lines_before_buffer.clear()
        return output[0][0] if len(output) > 0 else None, [item[1] for item in output]

    def get_maximum_index_length(self, data:list[tuple[Diff.Diff[Con.Don[int]], Diff.Diff[Con.Don[str]]]]) -> int:
        old_lines = 0
        new_lines = 0
        for index, line in data:
            if index.value_exists_at(0):
                old_lines += 1
            if index.value_exists_at(1):
                new_lines += 1
        return math.ceil(math.log10(max(old_lines, new_lines) + 1))

    def format_line_number(self, old_index:int, new_index:int, show_old:bool, show_new:bool, maximum_index_length:int) -> str:
        old_index_string = str(old_index)
        if len(old_index_string) < maximum_index_length:
            old_index_string = " " * (maximum_index_length - len(old_index_string)) + old_index_string
        new_index_string = str(new_index)
        if len(new_index_string) < maximum_index_length:
            new_index_string = " " * (maximum_index_length - len(new_index_string)) + new_index_string
        return f"{old_index_string if show_old else " " * maximum_index_length} {new_index_string if show_new else " " * maximum_index_length}"

    # TODO: now that ICon tracks index changes, change this method to utilize that.
    def print_comparison(self, data: ICon.IDon[Diff.Diff[Con.Don[int]], Diff.Diff[Con.Don[str]], Sequence, Con.Con[int], Con.Con[str]], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> list[tuple[int, str]] | EllipsisType:
        output:list[LineDelegate.LineType] = []
        data_list = list(data.items())
        maximum_index_length = self.get_maximum_index_length(data_list) # determines the amount of spacing.
        # pre-text stuff takes the form of "[index] (+/-) [line]"
        space_count = maximum_index_length * 2 + 4 # space for an index, a space, another index, a space, the +/- indicator, and another space.
        output.append((0, f"{" " * space_count}'''"))
        change_addition_lines:list[LineDelegate.LineType] = [] # these are needed to store lines. Change lines are printed all at once in order.
        change_removal_lines :list[LineDelegate.LineType] = [] # so it does additions from changes first and then removals from changes.
        current_length, addition_length, removal_length = 0, 0, 0
        lines_before_buffer:list[tuple[int,LineDelegate.LineType]] = [] # lines before a change. Cleared each time used.
        lines_to_add:list[LineDelegate.LineType] = []
        lines_after_count:int|None = None if self.surrounding_line_count is None else 0
        last_line_index = -1 # controls where the "..." lines appear.
        last_change_line_index = -1 # since change lines are stored and then added out of order, this needs to be stored separately.
        old_index, new_index = 0, 0 # both are shown (one is shown if it's a diff); they are different.
        for index, (index_diff, line) in enumerate(data_list): # index is not for showing, but for random data purposes.
            with trace.enter_key(index_diff, line):
                if line.length > 1: # there is a change.
                    new_index += 1
                    old_index += 1
                    current_length += 1
                    change_addition_lines.append((0, f"{self.format_line_number(old_index, new_index, False, True, maximum_index_length)} + {line[1][1]}"))
                    change_removal_lines. append((0, f"{self.format_line_number(old_index, new_index, True, False, maximum_index_length)} - {line[0][0]}"))
                    last_change_line_index = index
                elif not line.value_exists_at(1) or not line.value_exists_at(0): # addition or removal
                    branch = 1 if line.value_exists_at(1) else 0
                    if branch == 1: # addition
                        new_index += 1
                        addition_length += 1
                        current_length += 1
                        show_old, show_new = False, True
                    else: # removal
                        old_index += 1
                        removal_length += 1
                        show_old, show_new = True, False
                    before_buffer_start_index, buffer_lines = self.get_before_buffer(lines_before_buffer)
                    if self.surrounding_line_count is not None and before_buffer_start_index is not None and last_line_index + 1 != before_buffer_start_index:
                        lines_to_add.append((0, f"{" " * space_count}..."))
                    lines_to_add.extend(buffer_lines)
                    lines_to_add.extend(change_addition_lines)
                    lines_to_add.extend(change_removal_lines)
                    change_addition_lines.clear(); change_removal_lines.clear()
                    lines_to_add.append((0, f"{self.format_line_number(old_index, new_index, show_old, show_new, maximum_index_length)} {"+" if branch == 1 else "-"} {line[branch][branch]}"))
                    lines_after_count = self.surrounding_line_count
                    last_line_index = index
                else: # no change
                    old_index += 1
                    new_index += 1
                    current_length += 1
                    if len(change_addition_lines) > 0:
                        before_buffer_start_index, buffer_lines = self.get_before_buffer(lines_before_buffer)
                        if self.surrounding_line_count is not None and before_buffer_start_index is not None and last_line_index + 1 != before_buffer_start_index:
                            lines_to_add.append((0, f"{" " * space_count}..."))
                        lines_to_add.extend(buffer_lines)
                        lines_to_add.extend(change_addition_lines)
                        lines_to_add.extend(change_removal_lines)
                        change_addition_lines.clear(); change_removal_lines.clear()
                        lines_after_count = self.surrounding_line_count
                        last_line_index = last_change_line_index
                    current_line = (0, f"{self.format_line_number(old_index, new_index, True, True, maximum_index_length)}   {line[0, 1][1]}")
                    # do not need to consider the "..." line for the following
                    # because it is either in show all lines mode or it is
                    # showing lines immediately after a change.
                    if lines_after_count is None:
                        lines_to_add.append(current_line)
                    elif lines_after_count > 0:
                        last_line_index = index
                        lines_to_add.append(current_line)
                        lines_after_count -= 1
                        last_line_index = index
                    else:
                        lines_before_buffer.append((index, current_line))
            output.extend(lines_to_add)
            lines_to_add.clear()

        # clear buffers
        if len(change_addition_lines) > 0:
            before_buffer_start_index, buffer_lines = self.get_before_buffer(lines_before_buffer)
            if self.surrounding_line_count is not None and before_buffer_start_index is not None and last_line_index + 1 != before_buffer_start_index:
                lines_to_add.append((0, f"{" " * space_count}..."))
            lines_to_add.extend(buffer_lines)
            output.extend(change_addition_lines)
            output.extend(change_removal_lines)
            change_addition_lines.clear(); change_removal_lines.clear()
            last_line_index = last_change_line_index
        if self.surrounding_line_count is not None and last_line_index != len(data_list) - 1:
            output.append((0, f"{" " * space_count}..."))

        output.append((0, f"{" " * space_count}'''"))
        if self.measure_length:
            output = [(0, f"Total {self.field}: {current_length} (+{addition_length}, -{removal_length})")] + output
        return output
