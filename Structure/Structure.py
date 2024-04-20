import enum
from typing import Any, Generic, TypeVar, Union

import Structure.DataPath as DataPath
import Structure.StructureSet as StructureSet
import Structure.StructureUtilities as SU
import Structure.Normalizer as Normalizer
import Structure.Trace as Trace

class StructureFailure(enum.Enum):
    choose_structure_failure = 0

a = TypeVar("a")

class Structure(Generic[a]):

    name:str
    field:str
    normalizer:list[Normalizer.Normalizer]|None

    def check_initialization_parameters(self) -> None: ...

    def modifier_modify(self, data:Any) -> None: ...

    def __repr__(self) -> str:
        return "<%s %s>" % (self.__class__.__name__, self.name)

    def choose_structure_flat(self, key, value:type) -> Union["Structure",None]: ...

    def print_single(self, key_str:str|int|None, data:a, message:str, output:list[SU.Line], printer:Union["Structure[a]",None]) -> list[Trace.ErrorTrace]:
        exceptions:list[Trace.ErrorTrace] = []
        if printer is None:
            stringified_data = SU.stringify(data)
            if key_str is None:
                output.append(SU.Line("%s %s %s.") % (message, self.field, stringified_data))
            else:
                output.append(SU.Line("%s %s %s of %s.") % (message, self.field, SU.stringify(key_str), stringified_data))
        else:
            substructure_output, new_exceptions = printer.print_text(data)
            for exception in new_exceptions: exception.add(self.name, key_str)
            exceptions.extend(new_exceptions)
            match len(substructure_output), key_str is None:
                case 0, True:
                    output.append(SU.Line("%s empty %s.") % (message, self.field))
                case 0, False:
                    output.append(SU.Line("%s empty %s %s.") % (message, self.field, SU.stringify(key_str)))
                case 1, True:
                    output.append(SU.Line("%s %s %s.") % (message, self.field, substructure_output[0]))
                case 1, False:
                    output.append(SU.Line("%s %s %s of %s.") % (message, self.field, SU.stringify(key_str), substructure_output[0]))
                case _, True:
                    output.append(SU.Line("%s %s:") % (message, self.field))
                    output.extend(line.indent() for line in substructure_output)
                case _, False:
                    output.append(SU.Line("%s %s %s:") % (message, self.field, SU.stringify(key_str)))
                    output.extend(line.indent() for line in substructure_output)
        return exceptions

    def print_double(self, key_str:str|int|None, data1:a, data2:a, message:str, output:list[SU.Line], printers:"StructureSet.StructureSet") -> list[Trace.ErrorTrace]:
        exceptions:list[Trace.ErrorTrace] = []
        substructure_output1, new_exceptions = printers.print_text(0, data1)
        for exception in new_exceptions: exception.add(self.name, key_str)
        exceptions.extend(new_exceptions)
        substructure_output2, new_exceptions = printers.print_text(-1, data2) # [-1] because it must be the last item anyways.
        for exception in new_exceptions: exception.add(self.name, key_str)
        exceptions.extend(new_exceptions)
        if len(substructure_output1) == 0: substructure_output1 = [SU.Line("empty")]
        if len(substructure_output2) == 0: substructure_output2 = [SU.Line("empty")]
        match len(substructure_output1), len(substructure_output2), key_str is None:
            case 1, 1, True:
                output.append(SU.Line("%s %s from %s to %s.") % (message, self.field, substructure_output1[0], substructure_output2[0]))
            case 1, 1, False:
                output.append(SU.Line("%s %s %s from %s to %s.") % (message, self.field, SU.stringify(key_str), substructure_output1[0], substructure_output2[0]))
            case 1, _, True:
                output.append(SU.Line("%s %s from %s to:") % (message, self.field, substructure_output1[0]))
                output.extend(line.indent() for line in substructure_output2)
            case 1, _, False:
                output.append(SU.Line("%s %s %s from %s to:") % (message, self.field, SU.stringify(key_str), substructure_output1[0]))
                output.extend(line.indent() for line in substructure_output2)
            case _, 1, True:
                output.append(SU.Line("%s %s to %s from:") % (message, self.field, substructure_output2[0]))
                output.extend(line.indent() for line in substructure_output1)
            case _, 1, False:
                output.append(SU.Line("%s %s %s to %s from:") % (message, self.field, SU.stringify(key_str), substructure_output2[0]))
                output.extend(line.indent() for line in substructure_output1)
            case _, _, True:
                output.append(SU.Line("%s %s from:") % (message, self.field))
                output.extend(line.indent() for line in substructure_output1)
                output.append(SU.Line("to:"))
                output.extend(line.indent() for line in substructure_output2)
            case _, _, False:
                output.append(SU.Line("%s %s %s from:") % (message, self.field, SU.stringify(key_str)))
                output.extend(line.indent() for line in substructure_output1)
                output.append(SU.Line("to:"))
                output.extend(line.indent() for line in substructure_output2)
        return exceptions

    def check_all_types(self, data:a) -> list[Trace.ErrorTrace]: ...

    def compare_text(self, data:a) -> tuple[list[SU.Line],bool,list[Trace.ErrorTrace]]: ...

    def print_text(self, data:a) -> tuple[list[SU.Line],list[Trace.ErrorTrace]]: ...

    def normalize(self, data:a, normalizer_dependencies:Normalizer.LocalNormalizerDependencies, version_number:int) -> tuple[Any|None,list[Trace.ErrorTrace]]:
        raise NotImplementedError()

    def get_tag_paths(self, data:a, tag:str, data_path:DataPath.DataPath) -> tuple[list[DataPath.DataPath], list[Trace.ErrorTrace]]: ...

    def compare(self, data1:a, data2:a) -> tuple[a,list[Trace.ErrorTrace]]: ...

