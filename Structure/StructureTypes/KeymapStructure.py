from typing import Hashable, Sequence

from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.Structure import Structure
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Structure.StructureTag import StructureTag
from Structure.StructureTypes.MappingStructure import MappingStructure
from Utilities.Exceptions import StructureUnrecognizedKeyError
from Utilities.Trace import Trace


class KeymapStructure[K:Hashable, V, D, KBO, KCO, VBO, VCO, BO, CO](MappingStructure[K, V, D, KBO, KCO, VBO, VCO, BO, CO]):

    MIN_KEY_SIMILARITY_THRESHOLD = 0.0
    MIN_VALUE_SIMILARITY_THRESHOLD = 0.5
    KEY_WEIGHT = 0
    VALUE_WEIGHT = 1

    __slots__ = (
        "allow_key_moves",
        "key_structure",
        "key_weight",
        "similarity_weights",
        "value_structures",
        "value_tags",
        "value_types",
        "value_weights",
    )

    def link_keymap_structure(
        self,
        allow_key_moves:bool,
        allow_same_key_optimization:bool,
        key_structure:Structure[K, Con[K], Don[K], Don[K]|Diff[Don[K]], KBO, KCO]|None,
        key_weight:int,
        similarity_weights:dict[str,int],
        value_structures:dict[str,Structure[V, Con[V], Don[V], Don[V]|Diff[Don[V]], VBO, VCO]|None],
        value_tags:dict[str,set[StructureTag]],
        value_types:dict[str,tuple[type,...]],
        value_weights:dict[str,int],
    ) -> None:
        self.allow_key_moves = allow_key_moves
        self.allow_same_key_optimization = allow_same_key_optimization
        self.key_moves_ever_allowed = allow_key_moves
        self.key_structure = key_structure
        self.key_weight = key_weight
        self.similarity_weights = similarity_weights
        self.value_structures = value_structures
        self.value_tags = value_tags
        self.value_types = value_types
        self.value_weights = value_weights

    def get_key_structure(self, key: K, value: V, trace: Trace, environment: PrinterEnvironment) -> Structure[K, Con[K], Don[K], Don[K]|Diff[Don[K]], KBO, KCO]|None:
        return self.key_structure

    def get_value_structure(self, key: K, value: V, trace: Trace, environment: PrinterEnvironment) -> Structure[V, Con[V], Don[V], Don[V]|Diff[Don[V]], VBO, VCO]|None:
        if (output := self.value_structures.get(self.key_function(key), ...)) is ...:
            trace.exception(StructureUnrecognizedKeyError(key))
            return None
        return output

    def iter_structures(self) -> Sequence[Structure]:
        output:list[Structure] = []
        if self.key_structure is not None:
            output.append(self.key_structure)
        output.extend(structure for structure in self.value_structures.values() if structure is not None)
        return output

    def get_value_types(self, key: K, value: V, trace: Trace, environment: PrinterEnvironment) -> tuple[type, ...]:
        if (output := self.value_types.get(self.key_function(key), ...)) is ...:
            trace.exception(StructureUnrecognizedKeyError(key))
            return (object,) # catches everything. Ensures that additional, unnecessary errors don't occur.
        return output

    def get_value_tags(self, key: K, value: V, trace: Trace, environment: PrinterEnvironment) -> set[StructureTag]|None:
        return self.value_tags.get(self.key_function(key))

    def allow_key_move(self, key1: Con[K], key2: Con[K], value1: Con[V], value2: Con[V], branch1: int, branch2: int, trace: Trace, environment: ComparisonEnvironment) -> bool:
        if not self.allow_key_moves:
            return False
        structure1 = self.get_value_structure_chain_end(key1, value1, trace, environment[branch1])
        structure2 = self.get_value_structure_chain_end(key2, value2, trace, environment[branch2])
        return structure1 is structure2

    def get_similarity_weight(self, key: Con[K], value: Con[V], trace: Trace, environment: ComparisonEnvironment) -> int:
        if (output := self.similarity_weights.get(self.key_function(key.data), ...)) is ...:
            trace.exception(StructureUnrecognizedKeyError(key.data))
            return 1
        return output

    def get_key_weight(self, key: Con[K], value: Con[V], trace: Trace, environment: ComparisonEnvironment) -> int:
        return self.key_weight

    def get_value_weight(self, key: Con[K], value: Con[V], trace: Trace, environment: ComparisonEnvironment) -> int:
        if (output := self.value_weights.get(self.key_function(key.data), ...)) is ...:
            trace.exception(StructureUnrecognizedKeyError(key.data))
            return 1
        return output
