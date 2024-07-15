from typing import Any, Iterable, TypeVar

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

        self.structure:Structure.Structure[a]|None = None
        self.types:tuple[type,...]|None = None
        self.normalizer:list[Normalizer.Normalizer]|None = None
        self.post_normalizer:list[Normalizer.Normalizer]|None = None
        self.pre_normalized_types:tuple[type,...]|None = None

    def link_substructures(
        self,
        structure:Structure.Structure[a]|None,
        types:tuple[type,...],
        normalizer:list[Normalizer.Normalizer],
        post_normalizer:list[Normalizer.Normalizer],
        pre_normalized_types:tuple[type,...],
    ) -> None:
        self.structure = structure
        self.types = types
        self.normalizer = normalizer
        self.post_normalizer = post_normalizer
        self.pre_normalized_types = pre_normalized_types

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
            output.extend(exception.add(self.name, None) for exception in self.structure.check_all_types(data, environment))
        return output

    def normalize(self, data:a, environment:StructureEnvironment.StructureEnvironment) -> tuple[Any|None, list[Trace.ErrorTrace]]:
        if not self.children_has_normalizer: return None, []
        if self.normalizer is None:
            raise Exceptions.AttributeNoneError("normalizer", self)
        if self.post_normalizer is None:
            raise Exceptions.AttributeNoneError("post_normalizer", self)
        if self.pre_normalized_types is None:
            raise Exceptions.AttributeNoneError("pre_normalized_types", self)
        exceptions:list[Trace.ErrorTrace] = []
        if not isinstance(data, self.pre_normalized_types):
            exceptions.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.pre_normalized_types, type(data), "Data", "(pre-normalized)"), self.name, None, data))

        data_identity_changed = False
        for normalizer in self.normalizer:
            try:
                normalizer_output = normalizer(data)
                if normalizer_output is not None:
                    data_identity_changed = True
                    data = normalizer_output
            except Exception as e:
                return None, [Trace.ErrorTrace(e, self.name, None, data)]

        if self.structure is not None:
            normalizer_output, new_exceptions = self.structure.normalize(data, environment)
            exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
            if normalizer_output is not None:
                data_identity_changed = True
                data = normalizer_output

        for normalizer in self.post_normalizer:
            try:
                normalizer_output = normalizer(data)
                if normalizer_output is not None:
                    data_identity_changed = True
                    data = normalizer_output
            except Exception as e:
                return None, [Trace.ErrorTrace(e, self.name, None, data)]

        if data_identity_changed:
            return data, exceptions
        else:
            return None, exceptions

    def get_tag_paths(self, data:a, tag: str, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath], list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        exceptions:list[Trace.ErrorTrace] = []
        if self.structure is None:
            return [], exceptions
        output, new_exceptions = self.structure.get_tag_paths(data, tag, data_path.copy(), environment)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        return output, exceptions

    def get_similarity(self, data1: a, data2: a, environment:StructureEnvironment.StructureEnvironment) -> float:
        if self.structure is None:
            return float(data1 == data2)
        else:
            return self.structure.get_similarity(data1, data2, environment)

    def compare(self, data1:a, data2:a, environment:StructureEnvironment.StructureEnvironment) -> tuple[a|D.Diff[a, a], bool, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        if self.structure is None:
            if data1 is data2 or data1 == data2:
                output, has_changes = data1, False
            else:
                output, has_changes = D.Diff(data1, data2), True
        else:
            output, has_changes, new_exceptions = self.structure.compare(data1, data2, environment)
            exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        return output, has_changes, exceptions

    def print_text(self, data: a, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line], list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        if self.structure is None:
            output = [SU.Line(SU.stringify(data))]
        else:
            output, new_exceptions = self.structure.print_text(data, environment)
            exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
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
            exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
            return output, True, exceptions
        else:
            if self.structure is None:
                output = []
                has_changes = False
                pass # guaranteed no changes in here.
            else:
                output, has_changes, new_exceptions = self.structure.compare_text(data, environment)
                exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
            return output, has_changes, exceptions
