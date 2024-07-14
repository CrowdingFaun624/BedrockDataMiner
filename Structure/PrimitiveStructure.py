from typing import Any, Iterable, TypeVar, cast

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureUtilities as SU
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

d = TypeVar("d")

class PrimitiveStructure(Structure.Structure[d]):
    """
    Structure with no substructure.
    """

    def __init__(self, name: str, children_has_normalizer: bool, children_tags: set[str]) -> None:
        super().__init__(name, name, children_has_normalizer, children_tags)

        self.types:tuple[type,...]|None = None
        self.normalizer:list[Normalizer.Normalizer]|None = None
        self.pre_normalized_types:tuple[type,...]|None = None
        self.tags:list[str]|None = None

    def link_substructures(
        self,
        types:tuple[type,...],
        normalizer:list[Normalizer.Normalizer],
        pre_normalized_types:tuple[type,...],
        tags:list[str],
    ) -> None:
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

    def compare_text(self, data: d|D.Diff[d,d], environment: StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line], bool, list[Trace.ErrorTrace]]:
        if isinstance(data, D.Diff):
            has_changes = True
            match data.change_type:
                case D.ChangeType.addition:
                    output = [SU.Line("Added %s.") % (SU.stringify(data.new),)]
                case D.ChangeType.change:
                    output = [SU.Line("Changed from %s to %s." % (SU.stringify(data.old), SU.stringify(data.new)))]
                case D.ChangeType.removal:
                    output = [SU.Line("Removed %s." % (SU.stringify(data.old)))]
        else:
            has_changes = False
            output = []
        return output, has_changes, []

    def print_text(self, data: d, environment: StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line], list[Trace.ErrorTrace]]:
        return [SU.Line(SU.stringify(data))], []

    def normalize(self, data: d, environment: StructureEnvironment.StructureEnvironment) -> tuple[Any | None, list[Trace.ErrorTrace]]:
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
            data = cast(d, normalizer_output)
        return data, exceptions

    def get_tag_paths(self, data: d, tag: str, data_path: DataPath.DataPath, environment: StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath], list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        if self.tags is None:
            raise Exceptions.AttributeNoneError("tags", self)
        if tag in self.tags:
            return [data_path.copy().embed(data)], []
        else:
            return [], []

    def compare(self, data1: d, data2: d, environment: StructureEnvironment.StructureEnvironment) -> tuple[d, bool, list[Trace.ErrorTrace]]:
        if data1 is data2 or data1 == data2:
            return data1, False, []
        else:
            return cast(d, D.Diff(old=data1, new=data2)), True, []

    def get_similarity(self, data1: d, data2: d, environment:StructureEnvironment.StructureEnvironment) -> float:
        return float(data1 == data2)
