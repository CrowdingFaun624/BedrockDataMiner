from typing import Hashable, Sequence

import Structure.Container as Con
import Structure.Difference as Diff
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureTypes.MappingStructure as MappingStructure
import Utilities.Trace as Trace


class DictStructure[K:Hashable, V, D, KBO, KCO, VBO, VCO, BO, CO](MappingStructure.MappingStructure[K, V, D, KBO, KCO, VBO, VCO, BO, CO]):

    MIN_KEY_SIMILARITY_THRESHOLD = 0.0
    MIN_VALUE_SIMILARITY_THRESHOLD = 0.5
    KEY_WEIGHT = 2
    VALUE_WEIGHT = 8

    __slots__ = (
        "allow_key_moves",
        "key_structure",
        "key_weight",
        "value_structure",
        "value_types",
        "value_weight",
    )

    def link_dict_structure(
        self,
        allow_key_moves:bool,
        allow_same_key_optimization:bool,
        key_structure:Structure.Structure[K, Con.Con[K], Con.Don[K], Con.Don[K]|Diff.Diff[Con.Don[K]], KBO, KCO]|None,
        key_weight:int,
        value_structure:Structure.Structure[V, Con.Con[V], Con.Don[V], Con.Don[V]|Diff.Diff[Con.Don[V]], VBO, VCO]|None,
        value_types:tuple[type, ...],
        value_weight:int,
    ) -> None:
        self.allow_key_moves = allow_key_moves
        self.key_moves_ever_allowed = allow_key_moves
        self.allow_same_key_optimization = allow_same_key_optimization
        self.key_structure = key_structure
        self.key_weight = key_weight
        self.value_structure = value_structure
        self.value_types = value_types
        self.value_weight = value_weight

    def get_key_structure(self, key: K, value: V, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> Structure.Structure[K, Con.Con[K], Con.Don[K], Con.Don[K]|Diff.Diff[Con.Don[K]], KBO, KCO]|None:
        return self.key_structure

    def get_value_structure(self, key: K, value: V, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> Structure.Structure[V, Con.Con[V], Con.Don[V], Con.Don[V]|Diff.Diff[Con.Don[V]], VBO, VCO]|None:
        return self.value_structure

    def get_value_types(self, key: K, value: V, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> tuple[type, ...]:
        return self.value_types

    def allow_key_move(self, key1: Con.Con[K], key2: Con.Con[K], value1: Con.Con[V], value2: Con.Con[V], branch1:int, branch2:int, trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> bool:
        return self.allow_key_moves

    def get_key_weight(self, key: Con.Con[K], value: Con.Con[V], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> int:
        return self.key_weight

    def get_value_weight(self, key: Con.Con[K], value: Con.Con[V], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> int:
        return self.value_weight

    def iter_structures(self) -> Sequence[Structure.Structure]:
        output:list[Structure.Structure] = []
        if self.key_structure is not None:
            output.append(self.key_structure)
        if self.value_structure is not None:
            output.append(self.value_structure)
        return output
