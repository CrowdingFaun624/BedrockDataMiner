import enum
from typing import Any, Generic, Iterable, TypeVar, Union

import Structure.DataPath as DataPath
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureSet as StructureSet
import Structure.StructureUtilities as SU
import Structure.Trace as Trace


class StructureFailure(enum.Enum):
    choose_structure_failure = 0

a = TypeVar("a")

class Structure(Generic[a]):
    "Modular piece that generates comparison reports of data."

    def __init__(self, name:str, field:str, children_has_normalizer:bool, children_tags:set[str]) -> None:
        '''
        :name: The name of the Structure.
        :field: The string used to describe data with.
        :children_has_normalizer: If this Structure or its descendants has a Normalizer.
        :children_tags: The tags that this Structure or its descendants have.
        '''
        self.name = name
        self.field = field
        self.children_has_normalizer = children_has_normalizer
        self.children_tags = children_tags

    def __repr__(self) -> str:
        return "<%s %s>" % (self.__class__.__name__, self.name)

    def __hash__(self) -> int:
        return id(self)

    def clear_caches(self, memo:set["Structure"]) -> None:
        '''
        Clears all the caches of this Structure and of its children.
        :memo: The set of Structures already cleared.
        '''
        for substructure in self.iter_structures():
            if substructure in memo:
                continue
            memo.add(self)
            substructure.clear_caches(memo)

    def print_single(self, key_str:str|int|None, data:a, message:str, output:list[SU.Line], printer:Union["Structure",None], environment:StructureEnvironment.StructureEnvironment, *, post_message:str="") -> list[Trace.ErrorTrace]:
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
            stringified_data = SU.stringify(data)
            if key_str is None:
                output.append(SU.Line("%s %s%s %s.") % (message, self.field, post_message, stringified_data))
            else:
                output.append(SU.Line("%s %s%s %s of %s.") % (message, self.field, post_message, SU.stringify(key_str), stringified_data))
        else:
            substructure_output, new_exceptions = printer.print_text(data, environment)
            exceptions.extend(exception.add(self.name, key_str) for exception in new_exceptions)
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

    def print_double(
        self,
        key_str:str|int|None,
        data1:a,
        data2:a,
        message:str,
        output:list[SU.Line],
        printers:Union["StructureSet.StructureSet", "Structure", None],
        environment:StructureEnvironment.StructureEnvironment,
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
        :printer: The Structure (or None) to print the data with.
        :environment: The StructureEnvironment to use.
        :post_message: A string to put after the field.
        '''
        if printers is None:
            printer1 = None
            printer2 = None
        elif isinstance(printers, Structure):
            printer1 = printers
            printer2 = printers
        else:
            printer1 = printers[0]
            printer2 = printers[-1] # [-1] because it must be the last item anyways.
        exceptions:list[Trace.ErrorTrace] = []
        if printer1 is None:
            substructure_output1 = [SU.Line(SU.stringify(data1))]
        else:
            substructure_output1, new_exceptions = printer1.print_text(data1, environment)
            exceptions.extend(exception.add(self.name, key_str) for exception in new_exceptions)
        if printer2 is None:
            substructure_output2 = [SU.Line(SU.stringify(data2))]
        else:
            substructure_output2, new_exceptions = printer2.print_text(data2, environment)
            exceptions.extend(exception.add(self.name, key_str) for exception in new_exceptions)
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

    def check_all_types(self, data:a, environment:StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        '''
        Checks the types of the data using this Structure. Returns a list of ErrorTraces.
        :data: The data to check the types of.
        :environment: The StructureEnvironment to use.
        '''
        ...

    def compare_text(self, data:a, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line],bool,list[Trace.ErrorTrace]]:
        '''
        Generates lines from an object containing Diffs.
        Returns a list of Lines, if there were any changes, and a list of ErrorTraces.
        :data: The object containing Diffs.
        :environment: The StructureEnvironment to use.
        '''
        ...

    def print_text(self, data:a, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line],list[Trace.ErrorTrace]]:
        '''
        Generates lines from an object containing no Diffs.
        Returns a list of Lines and a list of ErrorTraces.
        :data: The object containing no Diffs.
        :environment: The StructureEnvironment to use.
        '''
        ...

    def normalize(self, data:a, environment:StructureEnvironment.StructureEnvironment) -> tuple[Any|None,list[Trace.ErrorTrace]]:
        '''
        Manipulates the data before comparison.
        Returns the normalized data and a list of list of ErrorTraces.
        :data: The data to manipulate.
        :environment: The StructureEnvironment to use.
        '''
        ...

    def get_tag_paths(self, data:a, tag:str, data_path:DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath], list[Trace.ErrorTrace]]:
        '''
        Returns the DataPaths on which the given tag exists in the Structure for the given data and a list of ErrorTraces.
        :data: The data to get the tag paths from.
        :tag: The tag to search for.
        :data_path: The current path of data traversed through the Structures so far.
        :environment: The StructureEnvironment to use.
        '''
        ...

    def compare(self, data1:a, data2:a, environment:StructureEnvironment.StructureEnvironment) -> tuple[a,bool,list[Trace.ErrorTrace]]:
        '''
        Combines the data into a single object with Diffs in it. Returns the combined object and if there are any differences.
        :data1: The data from the oldest Version.
        :data2: The data from the newest Version.
        :environment: The StructureEnvironment to use.
        '''
        ...

    def get_similarity(self, data1:a, data2:a, environment:StructureEnvironment.StructureEnvironment) -> float:
        '''
        Returns the similarity of data1 to data2. Is at most the greater of the complexities of the data.
        :data1: The data from the oldest Version.
        :data2: The data from the newest Version.
        :environment: The StructureEnvironment to use.
        '''
        ...

    def iter_structures(self) -> Iterable["Structure"]:
        '''Returns an Iterable of this Structure's substructures.'''
        ...
