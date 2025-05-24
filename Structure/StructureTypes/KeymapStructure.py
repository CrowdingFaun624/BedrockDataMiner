from typing import Hashable, Sequence

import Structure.Container as Con
import Structure.Difference as Diff
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureTag as StructureTag
import Structure.StructureTypes.MappingStructure as MappingStructure
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace


class KeymapStructure[K:Hashable, V, D, KBO, KCO, VBO, VCO, BO, CO](MappingStructure.MappingStructure[K, V, D, KBO, KCO, VBO, VCO, BO, CO]):

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
        key_structure:Structure.Structure[K, Con.Con[K], Con.Don[K], Con.Don[K]|Diff.Diff[Con.Don[K]], KBO, KCO]|None,
        key_weight:int,
        similarity_weights:dict[str,int],
        value_structures:dict[str,Structure.Structure[V, Con.Con[V], Con.Don[V], Con.Don[V]|Diff.Diff[Con.Don[V]], VBO, VCO]|None],
        value_tags:dict[str,set[StructureTag.StructureTag]],
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

    def get_key_structure(self, key: K, value: V, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> Structure.Structure[K, Con.Con[K], Con.Don[K], Con.Don[K]|Diff.Diff[Con.Don[K]], KBO, KCO]|None:
        return self.key_structure

    def get_value_structure(self, key: K, value: V, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> Structure.Structure[V, Con.Con[V], Con.Don[V], Con.Don[V]|Diff.Diff[Con.Don[V]], VBO, VCO]|None:
        if (output := self.value_structures.get(self.key_function(key), ...)) is ...:
            trace.exception(Exceptions.StructureUnrecognizedKeyError(key))
            return None
        return output

    def iter_structures(self) -> Sequence[Structure.Structure]:
        output:list[Structure.Structure] = []
        if self.key_structure is not None:
            output.append(self.key_structure)
        output.extend(structure for structure in self.value_structures.values() if structure is not None)
        return output

    def get_value_types(self, key: K, value: V, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> tuple[type, ...]:
        if (output := self.value_types.get(self.key_function(key), ...)) is ...:
            trace.exception(Exceptions.StructureUnrecognizedKeyError(key))
            return (object,) # catches everything. Ensures that additional, unnecessary errors don't occur.
        return output

    def get_value_tags(self, key: K, value: V, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> set[StructureTag.StructureTag]|None:
        return self.value_tags.get(self.key_function(key))

    def allow_key_move(self, key1: Con.Con[K], key2: Con.Con[K], value1: Con.Con[V], value2: Con.Con[V], branch1: int, branch2: int, trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> bool:
        if not self.allow_key_moves:
            return False
        structure1 = self.get_value_structure(key1.data, value1.data, trace, environment[branch1])
        structure2 = self.get_value_structure(key2.data, value2.data, trace, environment[branch2])
        return structure1 is structure2

    def get_similarity_weight(self, key: Con.Con[K], value: Con.Con[V], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> int:
        if (output := self.similarity_weights.get(self.key_function(key.data), ...)) is ...:
            trace.exception(Exceptions.StructureUnrecognizedKeyError(key.data))
            return 1
        return output

    def get_key_weight(self, key: Con.Con[K], value: Con.Con[V], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> int:
        return self.key_weight

    def get_value_weight(self, key: Con.Con[K], value: Con.Con[V], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> int:
        if (output := self.value_weights.get(self.key_function(key.data), ...)) is ...:
            trace.exception(Exceptions.StructureUnrecognizedKeyError(key.data))
            return 1
        return output
