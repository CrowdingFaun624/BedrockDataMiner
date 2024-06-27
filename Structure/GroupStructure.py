from typing import Any, Iterable, TypeVar

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureSet as StructureSet
import Structure.StructureUtilities as SU
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

a = TypeVar("a")

class GroupStructure(Structure.Structure[a]):

    def __init__(self, name: str, children_has_normalizer: bool, children_tags: set[str]) -> None:
        super().__init__(name, name, children_has_normalizer, children_tags)
        self.substructures:dict[type,Structure.Structure|None]|None = None
        self.types:tuple[type,...]|None = None

    def get_substructures(self) -> dict[type,Structure.Structure|None]:
        if self.substructures is None:
            raise Exceptions.AttributeNoneError("substructures", self)
        return self.substructures

    def get_types(self) -> tuple[type,...]:
        if self.types is None:
            raise Exceptions.AttributeNoneError("types", self)
        return self.types

    def link_substructures(
        self,
        substructures:dict[type,Structure.Structure|None],
        types:tuple[type,...],
    ) -> None:
        self.substructures = substructures
        self.types = types

    def iter_structures(self) -> Iterable[Structure.Structure]:
        yield from (substructure for substructure in self.get_substructures().values() if substructure is not None)

    def check_all_types(self, data: a, environment: StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        if not isinstance(data, self.get_types()):
            return [Trace.ErrorTrace(Exceptions.StructureTypeError(self.get_types(), type(data), "Data"), self.name, None, data)]
        else:
            return []

    def get_structure(self, data: a) -> tuple[Structure.Structure|None, list[Trace.ErrorTrace]]:
        output = self.get_substructures().get(type(data), Structure.StructureFailure.choose_structure_failure)
        if output is Structure.StructureFailure.choose_structure_failure:
            return None, [Trace.ErrorTrace(Exceptions.StructureTypeError(tuple(self.get_types()), type(data), "Data"), self.name, None, data)]
        else:
            return output, []

    def normalize(self, data: a, environment: StructureEnvironment.StructureEnvironment) -> tuple[Any | None, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        structure, new_exceptions = self.get_structure(data)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        if structure is None:
            return None, exceptions
        else:
            output, new_exceptions = structure.normalize(data, environment)
            exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
            return output, exceptions

    def get_tag_paths(self, data:a, tag: str, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        output:list[DataPath.DataPath] = []
        exceptions:list[Trace.ErrorTrace] = []
        structure, new_exceptions = self.get_structure(data)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        if structure is not None:
            new_tags, new_exceptions = structure.get_tag_paths(data, tag, data_path.copy(type(data)), environment)
            output.extend(new_tags)
            exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        return output, exceptions

    def choose_structure(self, data:a|D.Diff[a,a]) -> tuple[StructureSet.StructureSet, list[Trace.ErrorTrace]]:
        output:dict[D.DiffType,Structure.Structure|None] = {}
        exceptions:list[Trace.ErrorTrace] = []
        for item_iter, diff_type in D.iter_diff(data):
            structure = self.get_substructures().get(type(item_iter), Structure.StructureFailure.choose_structure_failure)
            if structure is Structure.StructureFailure.choose_structure_failure:
                exceptions.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.get_types(), type(data), "Data"), self.name, None, data))
                continue
            output[diff_type] = structure
        return StructureSet.StructureSet(output), exceptions

    def get_similarity(self, data1: a, data2: a) -> float:
        structure1, exceptions1 = self.get_structure(data1)
        structure2, exceptions2 = self.get_structure(data2)
        if len(exceptions1) > 0 or len(exceptions2) > 0:
            raise Exceptions.StructureExceptionError(self, self.get_similarity, exceptions1 + exceptions2)
        if structure1 is not structure2 or structure1 is None or structure2 is None:
            return 0.0
        else:
            return structure1.get_similarity(data1, data2)

    def compare(self, data1: a, data2: a, environment:StructureEnvironment.StructureEnvironment) -> tuple[a|D.Diff[a, a], bool, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        structure_set, new_exceptions = self.choose_structure(D.Diff(data1, data2))
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        output, has_changes, new_exceptions = structure_set.compare(data1, data2, environment)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        return output, has_changes, exceptions

    def print_text(self, data: a, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line], list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        structure, new_exceptions = self.choose_structure(data)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        output, new_exceptions = structure.print_text(D.DiffType.not_diff, data, environment)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        return output, exceptions

    def compare_text(self, data:a|D.Diff[a,a], environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line], bool, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        structure_set, new_exceptions = self.choose_structure(data)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        if isinstance(data, D.Diff):
            output:list[SU.Line] = []
            match data.change_type:
                case D.ChangeType.addition:
                    new_exceptions = self.print_single(None, data.new, "Added", output, structure_set[D.DiffType.new], environment)
                case D.ChangeType.change:
                    new_exceptions = self.print_double(None, data.old, data.new, "Changed", output, structure_set, environment)
                case D.ChangeType.removal:
                    new_exceptions = self.print_single(None, data.old, "Removed", output, structure_set[D.DiffType.old], environment)
            exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
            return output, True, exceptions
        elif len(structure_set) == 0:
            exceptions.append(Trace.ErrorTrace(Exceptions.StructureSetKeyError(D.DiffType.not_diff, structure_set), self.name, None, data))
            output, has_changes = [], False
        else:
            if structure_set[D.DiffType.not_diff] is None:
                output = []
                has_changes = False
                pass # guaranteed no changes in here.
            else:
                output, has_changes, new_exceptions = structure_set.compare_text(D.DiffType.not_diff, data, environment)
                exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        return output, has_changes, exceptions
