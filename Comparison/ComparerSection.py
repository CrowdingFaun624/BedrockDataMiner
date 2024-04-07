from typing import Any, Generic, TypeVar, Union

import Comparison.ComparerSet as ComparerSet
import Comparison.ComparisonUtilities as CU
import Comparison.Normalizer as Normalizer
import Comparison.Trace as Trace

a = TypeVar("a")

class ComparerSection(Generic[a]):

    name:str
    normalizer:list[Normalizer.Normalizer]|None

    def check_initialization_parameters(self) -> None: ...

    def modifier_modify(self, data:Any) -> None: ...

    def __repr__(self) -> str:
        return "<%s %s>" % (self.__class__.__name__, self.name)

    def choose_comparer_flat(self, key, value:type, trace:Trace.Trace) -> Union["ComparerSection",None]: ...

    def print_single(self, key_str:str|int|None, data:a, message:str, output:list[CU.Line], printer:Union["ComparerSection[a]",None], trace:Trace.Trace) -> None:
        if printer is None:
            stringified_data = CU.stringify(data)
            if key_str is None:
                output.append(CU.Line("%s %s %s.") % (message, self.name, stringified_data))
            else:
                output.append(CU.Line("%s %s %s of %s.") % (message, self.name, CU.stringify(key_str), stringified_data))
        else:
            subcomparer_output = printer.print_text(data, trace.copy(self.name, key_str))
            match len(subcomparer_output), key_str is None:
                case 0, True:
                    output.append(CU.Line("%s empty %s.") % (message, self.name))
                case 0, False:
                    output.append(CU.Line("%s empty %s %s.") % (message, self.name, CU.stringify(key_str)))
                case 1, True:
                    output.append(CU.Line("%s %s %s.") % (message, self.name, subcomparer_output[0]))
                case 1, False:
                    output.append(CU.Line("%s %s %s of %s.") % (message, self.name, CU.stringify(key_str), subcomparer_output[0]))
                case _, True:
                    output.append(CU.Line("%s %s:") % (message, self.name))
                    output.extend(line.indent() for line in subcomparer_output)
                case _, False:
                    output.append(CU.Line("%s %s %s:") % (message, self.name, CU.stringify(key_str)))
                    output.extend(line.indent() for line in subcomparer_output)

    def print_double(self, key_str:str|int|None, data1:a, data2:a, message:str, output:list[CU.Line], printers:"ComparerSet.ComparerSet", trace:Trace.Trace) -> None:
        new_trace = trace.copy(self.name, key_str)
        subcomparer_output1 = printers.print_text(0, data1, new_trace)
        subcomparer_output2 = printers.print_text(-1, data2, new_trace) # [-1] because it must be the last item anyways.
        if len(subcomparer_output1) == 0: subcomparer_output1 = [CU.Line("empty")]
        if len(subcomparer_output2) == 0: subcomparer_output2 = [CU.Line("empty")]
        match len(subcomparer_output1), len(subcomparer_output2), key_str is None:
            case 1, 1, True:
                output.append(CU.Line("%s %s from %s to %s.") % (message, self.name, subcomparer_output1[0], subcomparer_output2[0]))
            case 1, 1, False:
                output.append(CU.Line("%s %s %s from %s to %s.") % (message, self.name, CU.stringify(key_str), subcomparer_output1[0], subcomparer_output2[0]))
            case 1, _, True:
                output.append(CU.Line("%s %s from %s to:") % (message, self.name, subcomparer_output1[0]))
                output.extend(line.indent() for line in subcomparer_output2)
            case 1, _, False:
                output.append(CU.Line("%s %s %s from %s to:") % (message, self.name, CU.stringify(key_str), subcomparer_output1[0]))
                output.extend(line.indent() for line in subcomparer_output2)
            case _, 1, True:
                output.append(CU.Line("%s %s to %s from:") % (message, self.name, subcomparer_output2[0]))
                output.extend(line.indent() for line in subcomparer_output1)
            case _, 1, False:
                output.append(CU.Line("%s %s %s to %s from:") % (message, self.name, CU.stringify(key_str), subcomparer_output2[0]))
                output.extend(line.indent() for line in subcomparer_output1)
            case _, _, True:
                output.append(CU.Line("%s %s from:") % (message, self.name))
                output.extend(line.indent() for line in subcomparer_output1)
                output.append(CU.Line("to:"))
                output.extend(line.indent() for line in subcomparer_output2)
            case _, _, False:
                output.append(CU.Line("%s %s %s from:") % (message, self.name, CU.stringify(key_str)))
                output.extend(line.indent() for line in subcomparer_output1)
                output.append(CU.Line("to:"))
                output.extend(line.indent() for line in subcomparer_output2)

    def check_all_types(self, data:a, trace:Trace.Trace) -> list[tuple[Trace.Trace, Exception]]: ...

    def compare_text(self, data:a, trace:Trace.Trace) -> tuple[list[CU.Line],bool]: ...

    def print_text(self, data:a, trace:Trace.Trace) -> list[CU.Line]: ...

    def normalize(self, data:a, normalizer_dependencies:Normalizer.LocalNormalizerDependencies, version_number:int, trace:Trace.Trace) -> Any|None:
        raise NotImplementedError()

    def compare(self, data1:a, data2:a, trace:Trace.Trace) -> tuple[a,list[tuple[Trace.Trace,Exception]]]: ...

