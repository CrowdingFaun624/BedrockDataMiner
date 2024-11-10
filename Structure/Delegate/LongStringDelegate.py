import math

import Structure.AbstractIterableStructure as AbstractIterableStructure
import Structure.Delegate.DefaultDelegate as DefaultDelegate
import Structure.Difference as D
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace


class LongStringDelegate(DefaultDelegate.DefaultDelegate[int]):

    def __init__(
        self,
        structure:AbstractIterableStructure.AbstractIterableStructure|None,
        keys:dict[str,DefaultDelegate.DefaultDelegateKeysTypedDict],
        measure_length:bool=False,
        surrounding_line_count:int|None=5,
    ) -> None:
        super().__init__(structure, keys, "line", measure_length, False, False, False, None)

        self.surrounding_line_count = surrounding_line_count

    def print_text(self, data: list[str], environment: StructureEnvironment.PrinterEnvironment) -> tuple[list[DefaultDelegate.Line], list[Trace.ErrorTrace]]:
        if len(data) == 0:
            output = [DefaultDelegate.Line("empty")]
        else:
            output:list[DefaultDelegate.Line] = []
            output.append(DefaultDelegate.Line("'''"))
            for line in data:
                output.append(DefaultDelegate.Line(line))
            output.append(DefaultDelegate.Line("'''"))
        return output, []

    def get_before_buffer(self, lines_before_buffer:list[tuple[int,DefaultDelegate.Line]]) -> tuple[int|None, list[DefaultDelegate.Line]]:
        if self.surrounding_line_count is None:
            output = lines_before_buffer[:]
        elif len(lines_before_buffer) < self.surrounding_line_count:
            output = lines_before_buffer[:]
        else:
            output = lines_before_buffer[-self.surrounding_line_count:]
        lines_before_buffer.clear()
        return output[0][0] if len(output) > 0 else None, [item[1] for item in output]

    def get_maximum_index_length(self, data:list[str|D.Diff[str,str]]) -> int:
        old_lines = 0
        new_lines = 0
        for item in data:
            if isinstance(data, D.Diff):
                match data.change_type:
                    case D.ChangeType.addition:
                        new_lines += 1
                    case D.ChangeType.change:
                        new_lines += 1
                        old_lines += 1
                    case D.ChangeType.removal:
                        new_lines += 1
                        old_lines += 1
            else:
                new_lines += 1
                old_lines += 1
        return math.ceil(math.log10(max(old_lines, new_lines) + 1))

    def format_line_number(self, old_index:int, new_index:int, show_old:bool, show_new:bool, maximum_index_length:int) -> str:
        old_index_string = str(old_index)
        if len(old_index_string) < maximum_index_length:
            old_index_string = " " * (maximum_index_length - len(old_index_string)) + old_index_string
        new_index_string = str(new_index)
        if len(new_index_string) < maximum_index_length:
            new_index_string = " " * (maximum_index_length - len(new_index_string)) + new_index_string
        return "%s %s" % (
            old_index_string if show_old else " " * maximum_index_length,
            new_index_string if show_new else " " * maximum_index_length,
        )

    def compare_text(self, data: list[str|D.Diff[str,str]], environment: StructureEnvironment.ComparisonEnvironment) -> tuple[list[DefaultDelegate.Line], bool, list[Trace.ErrorTrace]]:
        output:list[DefaultDelegate.Line] = []
        maximum_index_length = self.get_maximum_index_length(data) # determines the amount of spacing.
        # pre-text stuff takes the form of "[index] (+/-) [line]"
        space_count = maximum_index_length * 2 + 4 # space for an index, a space, another index, a space, the +/- indicator, and another space.
        output.append(DefaultDelegate.Line("%s'''") % (" " * space_count,))
        change_addition_lines:list[DefaultDelegate.Line] = [] # these are needed to store lines. Change lines are printed all at once in order.
        change_removal_lines :list[DefaultDelegate.Line] = [] # so it does additions from changes first and then removals from changes.
        has_changes = False
        current_length, addition_length, removal_length = 0, 0, 0
        lines_before_buffer:list[tuple[int,DefaultDelegate.Line]] = [] # lines before a change. Cleared each time used.
        lines_to_add:list[DefaultDelegate.Line] = []
        lines_after_count:int|None = None if self.surrounding_line_count is None else 0
        last_line_index = -1 # controls where the "..." lines appear.
        last_change_line_index = -1 # since change lines are stored and then added out of order, this needs to be stored separately.
        old_index, new_index = 0, 0 # both are shown (one is shown if it's a diff); they are different.
        for index, line in enumerate(data): # index is not for showing, but for random data purposes.
            if isinstance(line, D.Diff):
                has_changes = True
                match line.change_type:
                    case D.ChangeType.addition:
                        new_index += 1
                        addition_length += 1
                        current_length += 1
                        before_buffer_start_index, buffer_lines = self.get_before_buffer(lines_before_buffer)
                        if self.surrounding_line_count is not None and before_buffer_start_index is not None and last_line_index + 1 != before_buffer_start_index:
                            lines_to_add.append(DefaultDelegate.Line("%s..." % (" " * space_count)))
                        lines_to_add.extend(buffer_lines)
                        lines_to_add.extend(change_addition_lines)
                        lines_to_add.extend(change_removal_lines)
                        change_addition_lines.clear(); change_removal_lines.clear()
                        lines_to_add.append(DefaultDelegate.Line("%s + %s" % (self.format_line_number(old_index, new_index, False, True, maximum_index_length), line.new)))
                        lines_after_count = self.surrounding_line_count
                        last_line_index = index
                    case D.ChangeType.change:
                        new_index += 1
                        old_index += 1
                        current_length += 1
                        change_addition_lines.append(DefaultDelegate.Line("%s + %s" % (self.format_line_number(old_index, new_index, False, True, maximum_index_length), line.new)))
                        change_removal_lines. append(DefaultDelegate.Line("%s - %s" % (self.format_line_number(old_index, new_index, True, False, maximum_index_length), line.old)))
                        last_change_line_index = index
                    case D.ChangeType.removal:
                        old_index += 1
                        removal_length += 1
                        before_buffer_start_index, buffer_lines = self.get_before_buffer(lines_before_buffer)
                        if self.surrounding_line_count is not None and before_buffer_start_index is not None and last_line_index + 1 != before_buffer_start_index:
                            lines_to_add.append(DefaultDelegate.Line("%s..." % (" " * space_count)))
                        lines_to_add.extend(buffer_lines)
                        lines_to_add.extend(change_addition_lines)
                        lines_to_add.extend(change_removal_lines)
                        change_addition_lines.clear(); change_removal_lines.clear()
                        lines_to_add.append(DefaultDelegate.Line("%s - %s" % (self.format_line_number(old_index, new_index, True, False, maximum_index_length), line.old)))
                        lines_after_count = self.surrounding_line_count
                        last_line_index = index
            else: # line is not a diff
                old_index += 1
                new_index += 1
                current_length += 1
                if len(change_addition_lines) > 0:
                    before_buffer_start_index, buffer_lines = self.get_before_buffer(lines_before_buffer)
                    if self.surrounding_line_count is not None and before_buffer_start_index is not None and last_line_index + 1 != before_buffer_start_index:
                        lines_to_add.append(DefaultDelegate.Line("%s..." % (" " * space_count)))
                    lines_to_add.extend(buffer_lines)
                    lines_to_add.extend(change_addition_lines)
                    lines_to_add.extend(change_removal_lines)
                    change_addition_lines.clear(); change_removal_lines.clear()
                    lines_after_count = self.surrounding_line_count
                    last_line_index = last_change_line_index
                current_line = DefaultDelegate.Line("%s   %s" % (self.format_line_number(old_index, new_index, True, True, maximum_index_length), line))
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

        # stuff might have some stuff in it or something idk
        if len(change_addition_lines) > 0:
            before_buffer_start_index, buffer_lines = self.get_before_buffer(lines_before_buffer)
            if self.surrounding_line_count is not None and before_buffer_start_index is not None and last_line_index + 1 != before_buffer_start_index:
                lines_to_add.append(DefaultDelegate.Line("%s..." % (" " * space_count)))
            lines_to_add.extend(buffer_lines)
            output.extend(change_addition_lines)
            output.extend(change_removal_lines)
            change_addition_lines.clear(); change_removal_lines.clear()
            last_line_index = last_change_line_index
        if self.surrounding_line_count is not None and last_line_index != len(data) - 1:
            output.append(DefaultDelegate.Line("%s..." % (" " * space_count)))

        output.append(DefaultDelegate.Line("%s'''") % (" " * space_count,))
        if self.measure_length:
            output = [DefaultDelegate.Line("Total %s: %i (+%i, -%i)") % (self.field, current_length, addition_length, removal_length)] + output
        return output, has_changes, []
