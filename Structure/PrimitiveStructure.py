from typing import TYPE_CHECKING, Any, Iterable, Iterator, TypeVar, Union, cast

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureTag as StructureTag
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Delegate.Delegate as Delegate

d = TypeVar("d")

class PrimitiveStructure(Structure.Structure[d]):
    """
    Structure with no substructure.
    """

    def __init__(self, name: str, children_has_normalizer: bool) -> None:
        super().__init__(name, children_has_normalizer, False)

        self.types:tuple[type,...]|None = None
        self.normalizer:list[Normalizer.Normalizer]|None = None
        self.pre_normalized_types:tuple[type,...]|None = None
        self.tags:set[StructureTag.StructureTag]|None = None

    def link_substructures(
        self,
        delegate:Union["Delegate.Delegate", None],
        types:tuple[type,...],
        normalizer:list[Normalizer.Normalizer],
        pre_normalized_types:tuple[type,...],
        tags:set[StructureTag.StructureTag],
        children_tags:set[StructureTag.StructureTag],
    ) -> None:
        super().link_substructures(delegate, children_tags)
        self.types = types
        self.normalizer = normalizer
        self.pre_normalized_types = pre_normalized_types
        self.tags = tags

    def iter_structures(self) -> Iterable[Structure.Structure]:
        return []

    def check_all_types(self, data:d, environment: StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        if self.types is None:
            raise Exceptions.AttributeNoneError("types", self)
        if not isinstance(data, self.types):
            return [Trace.ErrorTrace(Exceptions.StructureTypeError(self.types, type(data), "Data"), self.name, None, data)]
        else:
            return []

    def compare_text(self, data: d|D.Diff[d,d], environment: StructureEnvironment.ComparisonEnvironment) -> tuple[Any, bool, list[Trace.ErrorTrace]]:
        if self.delegate is None:
            if environment.default_delegate is None:
                raise Exceptions.AttributeNoneError("delegate", self)
            else:
                return environment.default_delegate.compare_text(data, environment)
        else:
            return self.delegate.compare_text(data, environment)

    def print_text(self, data: d, environment: StructureEnvironment.PrinterEnvironment) -> tuple[Any, list[Trace.ErrorTrace]]:
        if self.delegate is None:
            return (str(data), []) if environment.default_delegate is None else environment.default_delegate.print_text(data, environment)
        else:
            return self.delegate.print_text(data, environment)

    def normalize(self, data: d, environment: StructureEnvironment.PrinterEnvironment) -> tuple[Any | None, list[Trace.ErrorTrace]]:
        if self.normalizer is None:
            raise Exceptions.AttributeNoneError("normalizer", self)
        if self.pre_normalized_types is None:
            raise Exceptions.AttributeNoneError("pre_normalized_types", self)
        exceptions:list[Trace.ErrorTrace] = []
        if not isinstance(data, self.pre_normalized_types):
            exceptions.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.pre_normalized_types, type(data), "Data", "(pre-normalized)"), self.name, None, data))
        for normalizer in self.normalizer:
            try:
                normalizer_output = normalizer(data)
            except Exception as e:
                exceptions.append(Trace.ErrorTrace(e, self.name, None, data))
                return None, exceptions
            if normalizer_output is None:
                exceptions.append(Trace.ErrorTrace(Exceptions.NormalizerNoneError(normalizer, self), self.name, None, data))
                return None, exceptions
            data = cast(d, normalizer_output)
        return data, exceptions

    def get_tag_paths(self, data: d, tag: StructureTag.StructureTag, data_path: DataPath.DataPath, environment: StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath], list[Trace.ErrorTrace]]:
        if self.children_tags is None:
            raise Exceptions.AttributeNoneError("children_tags", self)
        if tag not in self.children_tags: return [], []
        if self.tags is None:
            raise Exceptions.AttributeNoneError("tags", self)
        if tag in self.tags:
            return [data_path.copy().embed(data)], []
        else:
            return [], []

    def get_referenced_files(self, data: d, environment: StructureEnvironment.PrinterEnvironment) -> Iterator[int]:
        return; yield

    def compare(self, data1: d, data2: d, environment: StructureEnvironment.ComparisonEnvironment) -> tuple[d, bool, list[Trace.ErrorTrace]]:
        if data1 is data2 or data1 == data2:
            return data1, False, []
        else:
            return cast(d, D.Diff(old=data1, new=data2)), True, []

    def get_similarity(self, data1: d, data2: d, depth:int, max_depth:int|None, environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace]) -> float:
        return float(data1 == data2)
