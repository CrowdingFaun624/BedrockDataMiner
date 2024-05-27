import enum
from typing import Any, Generic, Iterable, TypeVar, Union

import Structure.DataPath as DataPath
import Structure.Normalizer as Normalizer
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureSet as StructureSet
import Structure.StructureUtilities as SU
import Structure.Trace as Trace


class StructureFailure(enum.Enum):
    choose_structure_failure = 0

a = TypeVar("a")

class Structure(Generic[a]):

    def __init__(self, name:str, field:str, normalizer:list[Normalizer.Normalizer]|None, children_has_normalizer:bool, children_tags:set[str]) -> None:
        self.name = name
        self.field = field
        self.normalizer = normalizer
        self.children_has_normalizer = children_has_normalizer
        self.children_tags = children_tags

    def finalize(self) -> None:
        self.check_initialization_parameters()

    def check_initialization_parameters(self) -> None: ...

    def __repr__(self) -> str:
        return "<%s %s>" % (self.__class__.__name__, self.name)

    def __hash__(self) -> int:
        return id(self)

    def clear_caches(self, memo:set["Structure"]) -> None:
        '''Clears all the caches of this Structure and of its children.'''
        for substructure in self.iter_structures():
            if substructure in memo:
                continue
            memo.add(self)
            substructure.clear_caches(memo)

    def choose_structure_flat(self, key, value_type:type, value) -> Union["Structure",None]: ...

    def print_single(self, key_str:str|int|None, data:a, message:str, output:list[SU.Line], printer:Union["Structure[a]",None], environment:StructureEnvironment.StructureEnvironment, *, post_message:str="") -> list[Trace.ErrorTrace]:
        exceptions:list[Trace.ErrorTrace] = []
        if printer is None:
            stringified_data = SU.stringify(data)
            if key_str is None:
                output.append(SU.Line("%s %s%s %s.") % (message, self.field, post_message, stringified_data))
            else:
                output.append(SU.Line("%s %s%s %s of %s.") % (message, self.field, post_message, SU.stringify(key_str), stringified_data))
        else:
            substructure_output, new_exceptions = printer.print_text(data, environment)
            for exception in new_exceptions: exception.add(self.name, key_str)
            exceptions.extend(new_exceptions)
            match len(substructure_output), key_str is None:
                case 0, True:
                    output.append(SU.Line("%s empty %s%s.") % (message, self.field, post_message))
                case 0, False:
                    output.append(SU.Line("%s empty %s%s %s.") % (message, self.field, post_message, SU.stringify(key_str)))
                case 1, True:
                    output.append(SU.Line("%s %s%s %s.") % (message, self.field, post_message, substructure_output[0]))
                case 1, False:
                    output.append(SU.Line("%s %s%s %s of %s.") % (message, self.field, post_message, SU.stringify(key_str), substructure_output[0]))
                case _, True:
                    output.append(SU.Line("%s %s%s:") % (message, self.field, post_message))
                    output.extend(line.indent() for line in substructure_output)
                case _, False:
                    output.append(SU.Line("%s %s%s %s:") % (message, self.field, post_message, SU.stringify(key_str)))
                    output.extend(line.indent() for line in substructure_output)
        return exceptions

    def print_double(self, key_str:str|int|None, data1:a, data2:a, message:str, output:list[SU.Line], printers:"StructureSet.StructureSet", environment:StructureEnvironment.StructureEnvironment, *, post_message:str="") -> list[Trace.ErrorTrace]:
        exceptions:list[Trace.ErrorTrace] = []
        substructure_output1, new_exceptions = printers.print_text(0, data1, environment)
        for exception in new_exceptions: exception.add(self.name, key_str)
        exceptions.extend(new_exceptions)
        substructure_output2, new_exceptions = printers.print_text(-1, data2, environment) # [-1] because it must be the last item anyways.
        for exception in new_exceptions: exception.add(self.name, key_str)
        exceptions.extend(new_exceptions)
        if len(substructure_output1) == 0: substructure_output1 = [SU.Line("empty")]
        if len(substructure_output2) == 0: substructure_output2 = [SU.Line("empty")]
        match len(substructure_output1), len(substructure_output2), key_str is None:
            case 1, 1, True:
                output.append(SU.Line("%s %s%s from %s to %s.") % (message, self.field, post_message, substructure_output1[0], substructure_output2[0]))
            case 1, 1, False:
                output.append(SU.Line("%s %s%s %s from %s to %s.") % (message, self.field, post_message, SU.stringify(key_str), substructure_output1[0], substructure_output2[0]))
            case 1, _, True:
                output.append(SU.Line("%s %s%s from %s to:") % (message, self.field, post_message, substructure_output1[0]))
                output.extend(line.indent() for line in substructure_output2)
            case 1, _, False:
                output.append(SU.Line("%s %s%s %s from %s to:") % (message, self.field, post_message, SU.stringify(key_str), substructure_output1[0]))
                output.extend(line.indent() for line in substructure_output2)
            case _, 1, True:
                output.append(SU.Line("%s %s%s to %s from:") % (message, self.field, post_message, substructure_output2[0]))
                output.extend(line.indent() for line in substructure_output1)
            case _, 1, False:
                output.append(SU.Line("%s %s%s %s to %s from:") % (message, self.field, post_message, SU.stringify(key_str), substructure_output2[0]))
                output.extend(line.indent() for line in substructure_output1)
            case _, _, True:
                output.append(SU.Line("%s %s%s from:") % (message, self.field, post_message))
                output.extend(line.indent() for line in substructure_output1)
                output.append(SU.Line("to:"))
                output.extend(line.indent() for line in substructure_output2)
            case _, _, False:
                output.append(SU.Line("%s %s%s %s from:") % (message, self.field, post_message, SU.stringify(key_str)))
                output.extend(line.indent() for line in substructure_output1)
                output.append(SU.Line("to:"))
                output.extend(line.indent() for line in substructure_output2)
        return exceptions

    def check_all_types(self, data:a, environment:StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]: ...

    def compare_text(self, data:a, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line],bool,list[Trace.ErrorTrace]]: ...

    def print_text(self, data:a, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line],list[Trace.ErrorTrace]]: ...

    def normalize(self, data:a, normalizer_dependencies:Normalizer.LocalNormalizerDependencies, version_number:int, environment:StructureEnvironment.StructureEnvironment) -> tuple[Any|None,list[Trace.ErrorTrace]]:
        raise NotImplementedError()

    def get_tag_paths(self, data:a, tag:str, data_path:DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath], list[Trace.ErrorTrace]]: ...

    def compare(self, data1:a, data2:a, environment:StructureEnvironment.StructureEnvironment) -> tuple[a,bool,list[Trace.ErrorTrace]]: ...

    def iter_structures(self) -> Iterable["Structure"]:
        '''Returns in Iterable of this Structure's substructures.'''
        ...
