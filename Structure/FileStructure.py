from typing import Any, TypeVar

import Serializer.Serializer as Serializer
import Structure.Delegate.Delegate as Delegate
import Structure.Normalizer as Normalizer
import Structure.PassthroughStructure as PassthroughStructure
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions
import Utilities.File as File

a = TypeVar("a")

class FileStructure(PassthroughStructure.PassthroughStructure[a]):

    def __init__(self, name: str, children_has_normalizer: bool, children_tags: set[str]) -> None:
        super().__init__(name, children_has_normalizer, children_tags)
        
        self.serializer:Serializer.Serializer[a,Any]|None = None

    def link_substructures(
        self,
        structure:Structure.Structure|None,
        delegate:Delegate.Delegate|None,
        serializer:Serializer.Serializer[a,Any],
        types:tuple[type,...],
        normalizer:list[Normalizer.Normalizer],
        post_normalizer:list[Normalizer.Normalizer],
        pre_normalized_types:tuple[type,...],
    ) -> None:
        super().link_substructures(structure, delegate, types, normalizer, post_normalizer, pre_normalized_types)
        
        self.serializer = serializer

    def normalize(self, data: File.File, environment:StructureEnvironment.StructureEnvironment) -> tuple[a|None, list[Trace.ErrorTrace]]:
        if self.serializer is None:
            raise Exceptions.AttributeNoneError("serializer", self)
        try:
            data_parsed = self.serializer.deserialize(data.read())
        except Exception as e:
            return None, [Trace.ErrorTrace(e, self.name, None, data)]
        new_output, exceptions = super().normalize(data_parsed, environment)
        if new_output is not None and new_output is not data_parsed:
            data_parsed = new_output
        return data_parsed, exceptions
