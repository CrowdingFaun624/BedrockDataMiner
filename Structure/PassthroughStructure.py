from typing import Iterable, TypeVar

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureUtilities as SU
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

a = TypeVar("a")

class PassthroughStructure(Structure.Structure[a]):
    '''
    Simply passes data through itself. Can be subclassed.
    Not all Structures that have this behavior have to subclass this class.
    '''

    def __init__(self, name: str, field: str, children_has_normalizer: bool, children_tags: set[str]) -> None:
        super().__init__(name, field, children_has_normalizer, children_tags)

        self.structure:Structure.Structure|None = None
        self.types:tuple[type,...]|None = None
        self.normalizer:list[Normalizer.Normalizer]|None = None

    def link_substructures(
        self,
        structure:Structure.Structure|None,
        types:list[type],
        normalizer:list[Normalizer.Normalizer],
    ) -> None:
        self.structure = structure
        self.types = tuple(types)
        self.normalizer = normalizer

    def iter_structures(self) -> Iterable[Structure.Structure]:
        if self.structure is None: return []
        else: return [self.structure]

    def check_all_types(self, data:a, environment:StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        output:list[Trace.ErrorTrace] = []
        if self.types is None:
            raise Exceptions.AttributeNoneError("types", self)
        if not isinstance(data, self.types):
            output.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.types, type(data), "Data"), self.name, None, data))
            return output
        if self.structure is not None:
            new_exceptions = self.structure.check_all_types(data, environment)
            for exception in new_exceptions: exception.add(self.name, None)
            output.extend(new_exceptions)
        return output

    def normalize(self, data:a, environment:StructureEnvironment.StructureEnvironment) -> tuple[None, list[Trace.ErrorTrace]]:
        if not self.children_has_normalizer: return None, []
        if self.normalizer is None:
            raise Exceptions.AttributeNoneError("normalizer", self)
        for normalizer in self.normalizer:
            try:
                normalizer(data)
            except Exception as e:
                return None, [Trace.ErrorTrace(e, self.name, None, data)]
        exceptions:list[Trace.ErrorTrace] = []
        if self.structure is not None:
            normalize_output, new_exceptions = self.structure.normalize(data, environment)
            for exception in new_exceptions: exception.add(self.name, None)
            exceptions.extend(new_exceptions)
            if normalize_output is not None:
                data = normalize_output
        return None, exceptions

    def get_tag_paths(self, data:a, tag: str, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath], list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        exceptions:list[Trace.ErrorTrace] = []
        if self.structure is None:
            return [], exceptions
        output, new_exceptions = self.structure.get_tag_paths(data, tag, data_path.copy(), environment)
        for exception in new_exceptions: exception.add(self.name, None)
        exceptions.extend(new_exceptions)
        return output, exceptions

    def compare(self, data1:a, data2:a, environment:StructureEnvironment.StructureEnvironment) -> tuple[a|D.Diff[a, a], bool, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        if self.structure is None:
            if data1 is data2 or data1 == data2:
                output, has_changes = data1, False
            else:
                output, has_changes = D.Diff(data1, data2), True
        else:
            output, has_changes, new_exceptions = self.structure.compare(data1, data2, environment)
            for exception in new_exceptions: exception.add(self.name, None)
            exceptions.extend(new_exceptions)
        return output, has_changes, exceptions

    def print_text(self, data: a, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line], list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        if self.structure is None:
            output = [SU.Line(SU.stringify(data))]
        else:
            output, new_exceptions = self.structure.print_text(data, environment)
            for exception in new_exceptions: exception.add(self.name, None)
            exceptions.extend(new_exceptions)
        return output, exceptions

    def compare_text(self, data:a|D.Diff[a,a], environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line], bool, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        if isinstance(data, D.Diff):
            output:list[SU.Line] = []
            match data.change_type:
                case D.ChangeType.addition:
                    new_exceptions = self.print_single(None, data.new, "Added", output, self.structure, environment)
                case D.ChangeType.change:
                    new_exceptions = self.print_double(None, data.old, data.new, "Changed", output, self.structure, environment)
                case D.ChangeType.removal:
                    new_exceptions = self.print_single(None, data.old, "Removed", output, self.structure, environment)
            for exception in new_exceptions: exception.add(self.name, None)
            exceptions.extend(new_exceptions)
            return output, True, exceptions
        else:
            if self.structure is None:
                output = []
                has_changes = False
                pass # guaranteed no changes in here.
            else:
                output, has_changes, new_exceptions = self.structure.compare_text(data, environment)
                for exception in new_exceptions: exception.add(self.name, None)
                exceptions.extend(new_exceptions)
            return output, has_changes, exceptions
