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
    ) -> None:
        super().__init__(structure, keys, "line", measure_length, False, False, None)

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

    def compare_text(self, data: list[str|D.Diff[str,str]], environment: StructureEnvironment.ComparisonEnvironment) -> tuple[list[DefaultDelegate.Line], bool, list[Trace.ErrorTrace]]:
        output:list[DefaultDelegate.Line] = []
        maximum_index_length = math.ceil(math.log10(len(data) + 1)) # determines the amount of spacing.
        # pre-text stuff takes the form of "[index] (+/-) [line]"
        space_count = maximum_index_length + 3
        output.append(DefaultDelegate.Line("%s'''") % (" " * space_count,))
        change_addition_lines:list[DefaultDelegate.Line] = [] # these are needed to store lines. Change lines are printed all at once in order.
        change_removal_lines :list[DefaultDelegate.Line] = [] # so it does additions from changes first and then removals from changes.
        has_changes = False
        current_length, addition_length, removal_length = 0, 0, 0
        for index, line in enumerate(data):
            index_string = str(index)
            if len(index_string) < maximum_index_length:
                index_string = " " * (maximum_index_length - len(index_string)) + index_string
            if isinstance(line, D.Diff):
                has_changes = True
                match line.change_type:
                    case D.ChangeType.addition:
                        addition_length += 1
                        current_length += 1
                        line_to_add = DefaultDelegate.Line("%s + %s" % (index_string, line.new))
                    case D.ChangeType.change:
                        current_length += 1
                        change_addition_lines.append(DefaultDelegate.Line("%s + %s" % (index_string, line.new)))
                        change_removal_lines .append(DefaultDelegate.Line("%s - %s" % (index_string, line.new)))
                        line_to_add = None
                    case D.ChangeType.removal:
                        removal_length += 1
                        line_to_add = DefaultDelegate.Line("%s - %s" % (index_string, line.old))
            else:
                current_length += 1
                line_to_add = DefaultDelegate.Line("%s   %s" % (index_string, line))
            if line_to_add is not None:
                output.extend(change_addition_lines)
                output.extend(change_removal_lines)
                output.append(line_to_add)
                change_addition_lines = []; change_removal_lines = []
        output.extend(change_addition_lines)
        output.extend(change_removal_lines)
        if self.measure_length:
            output = [DefaultDelegate.Line("Total %s: %i (+%i, -%i)") % (self.field, current_length, addition_length, removal_length)] + output
        return output, has_changes, []
