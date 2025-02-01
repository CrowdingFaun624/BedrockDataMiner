from typing import TYPE_CHECKING, Iterable, Sequence

import Structure.Normalizer as Normalizer
import Structure.PassthroughStructure as PassthroughStructure
import Structure.Structure as Structure
import Structure.StructureTag as StructureTag
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Delegate.Delegate as Delegate

class UnionStructure[a](PassthroughStructure.PassthroughStructure[a]):

    __slots__ = (
        "substructures",
    )

    def __init__(
        self,
        name: str,
        max_similarity_descendent_depth:int|None,
        max_similarity_ancestor_depth:int|None,
        children_has_normalizer: bool,
        children_has_garbage_collection:bool,
    ) -> None:
        super().__init__(name, max_similarity_ancestor_depth, max_similarity_descendent_depth, children_has_normalizer, children_has_garbage_collection)

        self.substructures:dict[type,Structure.Structure|None]

    def link_substructures(
        self,
        substructures:dict[type,Structure.Structure|None],
        delegate:"Delegate.Delegate|None",
        types:tuple[type,...],
        normalizer:Sequence[Normalizer.Normalizer],
        post_normalizer:Sequence[Normalizer.Normalizer],
        pre_normalized_types:tuple[type,...],
        children_tags:set[StructureTag.StructureTag],
    ) -> None:
        super().link_substructures(delegate, types, normalizer, post_normalizer, pre_normalized_types, children_tags)
        self.substructures = substructures

    def iter_structures(self) -> Iterable[Structure.Structure]:
        yield from (substructure for substructure in self.substructures.values() if substructure is not None)

    def get_structure(self, key:None, value: a) -> tuple[Structure.Structure|None, Sequence[Trace.ErrorTrace]]:
        output = self.substructures.get(type(value), ...)
        if output is ...:
            return None, (Trace.ErrorTrace(Exceptions.StructureTypeError(tuple(self.types), type(value), "Data"), self.name, None, value),)
        else:
            return output, ()
