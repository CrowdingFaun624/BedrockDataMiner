from typing import Hashable, Sequence

from ordered_set import OrderedSet

from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.Structure import Structure, convert_types_to_tuple, types_type
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Structure.StructureTypes.MappingStructure import MappingStructure
from Structure.Uses import NonEmptyUse, Region, StructureUse, TypeUse, Use
from Utilities.Trace import Trace


class DictStructure[K:Hashable, V, D, KBO, KCO, VBO, VCO, BO, CO](MappingStructure[K, V, D, KBO, KCO, VBO, VCO, BO, CO]):

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
        "value_type_list",
        "value_weight",
    )

    def link_dict_structure(
        self,
        allow_key_moves:bool,
        allow_same_key_optimization:bool,
        key_structure:Structure[K, Con[K], Don[K], Don[K]|Diff[Don[K]], KBO, KCO]|None,
        key_weight:int,
        value_structure:Structure[V, Con[V], Don[V], Don[V]|Diff[Don[V]], VBO, VCO]|None,
        value_types:types_type,
        value_weight:int,
    ) -> None:
        self.allow_key_moves = allow_key_moves
        self.key_moves_ever_allowed = allow_key_moves
        self.allow_same_key_optimization = allow_same_key_optimization
        self.key_structure = key_structure
        self.key_weight = key_weight
        self.value_structure = value_structure
        self.value_type_list = value_types
        self.value_weight = value_weight

    def finalize_dict_structure(self) -> None:
        self.value_types = convert_types_to_tuple(self.value_type_list)
        del self.value_type_list

    def get_key_structure(self, key: K, value: V, trace: Trace, environment: PrinterEnvironment) -> Structure[K, Con[K], Don[K], Don[K]|Diff[Don[K]], KBO, KCO]|None:
        return self.key_structure

    def get_value_structure(self, key: K, value: V, trace: Trace, environment: PrinterEnvironment) -> Structure[V, Con[V], Don[V], Don[V]|Diff[Don[V]], VBO, VCO]|None:
        return self.value_structure

    def get_value_types(self, key: K, value: V, trace: Trace, environment: PrinterEnvironment) -> tuple[type, ...]:
        return self.value_types

    def allow_key_move(self, key1: Con[K], key2: Con[K], value1: Con[V], value2: Con[V], branch1:int, branch2:int, trace: Trace, environment: ComparisonEnvironment) -> bool:
        return self.allow_key_moves

    def get_key_weight(self, key: Con[K], value: Con[V], trace: Trace, environment: ComparisonEnvironment) -> int:
        return self.key_weight

    def get_value_weight(self, key: Con[K], value: Con[V], trace: Trace, environment: ComparisonEnvironment) -> int:
        return self.value_weight

    def iter_structures(self) -> Sequence[Structure]:
        output:list[Structure] = []
        if self.key_structure is not None:
            output.append(self.key_structure)
        if self.value_structure is not None:
            output.append(self.value_structure)
        return output

    def get_all_uses(self, memo: set[Structure], parent_use:Use|None) -> OrderedSet[Use]:
        if self in memo: return OrderedSet(())
        output:OrderedSet[Use] = OrderedSet(())
        output.update(super().get_all_uses(memo, parent_use))
        non_empty_use = NonEmptyUse(self, None, StructureUse(self, None, parent_use))
        if self.key_structure is not None:
            output.update(self.key_structure.get_all_uses(memo, non_empty_use if self.key_structure.is_inline else None))
        if self.value_structure is not None:
            output.update(self.value_structure.get_all_uses(memo, non_empty_use if self.value_structure.is_inline else None))
        for value_type in self.value_types:
            output.add(TypeUse(value_type, Region.value_types, non_empty_use, None))
        return output
