from typing import TYPE_CHECKING, Any, Iterable, Iterator, Sequence, cast

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

class PrimitiveStructure[d](Structure.Structure[d]):
    """
    Structure with no substructure.
    """

    __slots__ = (
        "normalizer",
        "pre_normalized_types",
        "tags",
        "types",
    )

    def __init__(self, name: str, children_has_normalizer: bool) -> None:
        super().__init__(name, children_has_normalizer, False)

        self.types:tuple[type,...]
        self.normalizer:Sequence[Normalizer.Normalizer]
        self.pre_normalized_types:tuple[type,...]
        self.tags:set[StructureTag.StructureTag]

    def link_substructures(
        self,
        delegate:"Delegate.Delegate|None",
        types:tuple[type,...],
        normalizer:Sequence[Normalizer.Normalizer],
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
        return ()

    def check_all_types(self, data:d, environment: StructureEnvironment.StructureEnvironment) -> Sequence[Trace.ErrorTrace]:
        if not isinstance(data, self.types):
            return (Trace.ErrorTrace(Exceptions.StructureTypeError(self.types, type(data), "Data"), self.name, None, data),)
        else:
            return ()

    def compare_text(self, data: d|D.Diff[d], environment: StructureEnvironment.ComparisonEnvironment) -> tuple[Any, bool, Sequence[Trace.ErrorTrace]]:
        if self.delegate is None:
            if environment.default_delegate is None:
                raise Exceptions.InvalidStateError(self)
            else:
                return environment.default_delegate.compare_text(data, environment)
        else:
            return self.delegate.compare_text(data, environment)

    def print_text(self, data: d, environment: StructureEnvironment.PrinterEnvironment) -> tuple[Any, Sequence[Trace.ErrorTrace]]:
        if self.delegate is None:
            return (str(data), ()) if environment.default_delegate is None else environment.default_delegate.print_text(data, environment)
        else:
            return self.delegate.print_text(data, environment)

    def normalize(self, data: d, environment: StructureEnvironment.PrinterEnvironment) -> tuple[Any | None, Sequence[Trace.ErrorTrace]]:
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

    def get_tag_paths(self, data: d, tag: StructureTag.StructureTag, data_path: DataPath.DataPath, environment: StructureEnvironment.StructureEnvironment) -> tuple[Sequence[DataPath.DataPath], Sequence[Trace.ErrorTrace]]:
        if tag in self.tags:
            return (data_path.copy().embed(data),), ()
        else:
            return (), ()

    def get_referenced_files(self, data: d, environment: StructureEnvironment.PrinterEnvironment) -> Iterator[int]:
        return; yield

    def compare(self, data1: d, data2: d, environment: StructureEnvironment.ComparisonEnvironment, branch:int, branches:int) -> tuple[d|D.Diff[d], bool, Sequence[Trace.ErrorTrace]]:
        if not environment.is_multi_diff and (data1 is data2 or data1 == data2):
            return data1, False, ()
        else:
            # I fill into the past for a reason.
            # Imagine the parent is an AbstractMappingStructure. If value1 is a Diff, the branches of the below Diff will be thrown out anyways.
            # If value1 isn't a Diff, then I want a past-filled Diff that represents both value1 and value2; the below Diff satisfies that.
            return D.Diff(branches, {tuple(range(0,branch+1)): data1, (branch+1,): data2}), True, ()

    def get_similarity(self, data1: d, data2: d, depth:int, max_depth:int|None, environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace], branch:int) -> float:
        return float(data1 == data2)
