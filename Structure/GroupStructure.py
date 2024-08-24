from typing import TYPE_CHECKING, Any, Iterable, TypeVar, Union

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.PassthroughStructure as PassthroughStructure
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureSet as StructureSet
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Delegate.Delegate as Delegate

a = TypeVar("a")

class GroupStructure(PassthroughStructure.PassthroughStructure[a]):

    def __init__(self, name: str, children_has_normalizer: bool, children_tags: set[str]) -> None:
        super().__init__(name, children_has_normalizer, children_tags)

        self.substructures:dict[type,Structure.Structure|None]|None = None

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
        delegate:Union["Delegate.Delegate", None],
        types:tuple[type,...],
        normalizer:list[Normalizer.Normalizer],
        post_normalizer:list[Normalizer.Normalizer],
        pre_normalized_types:tuple[type,...],
    ) -> None:
        super().link_substructures(None, delegate, types, normalizer, post_normalizer, pre_normalized_types)
        self.substructures = substructures

    def iter_structures(self) -> Iterable[Structure.Structure]:
        yield from (substructure for substructure in self.get_substructures().values() if substructure is not None)

    def check_all_types(self, data: a, environment: StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        if not isinstance(data, self.get_types()):
            return [Trace.ErrorTrace(Exceptions.StructureTypeError(self.get_types(), type(data), "Data"), self.name, None, data)]
        else:
            return []

    def get_structure(self, key:None, value: a) -> tuple[Structure.Structure|None, list[Trace.ErrorTrace]]:
        output = self.get_substructures().get(type(value), ...)
        if output is ...:
            return None, [Trace.ErrorTrace(Exceptions.StructureTypeError(tuple(self.get_types()), type(value), "Data"), self.name, None, value)]
        else:
            return output, []

    def normalize(self, data: a, environment: StructureEnvironment.PrinterEnvironment) -> tuple[Any | None, list[Trace.ErrorTrace]]:
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
            if normalizer.version_range is not None and environment.get_version() not in normalizer.version_range: continue
            try:
                normalizer_output = normalizer(data)
                if normalizer_output is not None:
                    data_identity_changed = True
                    data = normalizer_output
            except Exception as e:
                exceptions.append(Trace.ErrorTrace(e, self.name, None, data))
                return None, exceptions

        structure, new_exceptions = self.get_structure(None, data)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        if structure is not None:
            normalizer_output, new_exceptions = structure.normalize(data, environment)
            exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
            if normalizer_output is not None:
                data_identity_changed = True
                data = normalizer_output

        for normalizer in self.post_normalizer:
            if normalizer.version_range is not None and environment.get_version() not in normalizer.version_range: continue
            try:
                normalizer_output = normalizer(data)
                if normalizer_output is not None:
                    data_identity_changed = True
                    data = normalizer_output
            except Exception as e:
                exceptions.append(Trace.ErrorTrace(e, self.name, None, data))
                return None, exceptions

        if data_identity_changed:
            return data, exceptions
        else:
            return None, exceptions

    def get_tag_paths(self, data:a, tag: str, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        output:list[DataPath.DataPath] = []
        exceptions:list[Trace.ErrorTrace] = []
        structure, new_exceptions = self.get_structure(None, data)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        if structure is not None:
            new_tags, new_exceptions = structure.get_tag_paths(data, tag, data_path.copy(type(data)), environment)
            output.extend(new_tags)
            exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        return output, exceptions

    def choose_structure(self, key:None, value:a|D.Diff[a,a]) -> tuple[StructureSet.StructureSet, list[Trace.ErrorTrace]]:
        output:dict[D.DiffType,Structure.Structure|None] = {}
        exceptions:list[Trace.ErrorTrace] = []
        for item_iter, diff_type in D.iter_diff(value):
            structure = self.get_substructures().get(type(item_iter), ...)
            if structure is ...:
                exceptions.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.get_types(), type(value), "Data"), self.name, None, value))
                continue
            output[diff_type] = structure
        return StructureSet.StructureSet(output), exceptions

    def get_similarity(self, data1: a, data2: a, environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace]) -> float:
        structure1, exceptions1 = self.get_structure(None, data1)
        structure2, exceptions2 = self.get_structure(None, data2)
        if len(exceptions1) > 0 or len(exceptions2) > 0:
            exceptions.append(Trace.ErrorTrace(Exceptions.StructureExceptionError(self, self.get_similarity, exceptions1 + exceptions2), self.name, None, (data1, data2)))
        if structure1 is not structure2 or structure1 is None or structure2 is None:
            return 0.0
        else:
            output = structure1.get_similarity(data1, data2, environment, exceptions)
            return output

    def compare(self, data1: a, data2: a, environment:StructureEnvironment.ComparisonEnvironment) -> tuple[a|D.Diff[a, a], bool, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        structure_set, new_exceptions = self.choose_structure(None, D.Diff(data1, data2))
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        output, has_changes, new_exceptions = structure_set.compare(data1, data2, environment)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        return output, has_changes, exceptions
