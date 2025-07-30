from typing import Hashable, Sequence

from ordered_set import OrderedSet

from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.IterableContainer import ICon
from Structure.Structure import Structure
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Structure.StructureTag import StructureTag
from Structure.StructureTypes.MappingStructure import MappingStructure
from Structure.Uses import (
    KeyUse,
    NonEmptyUse,
    Region,
    StructureUse,
    TypeUse,
    UsageTracker,
    Use,
)
from Utilities.Exceptions import StructureTypeError, StructureUnrecognizedKeyError
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
        "value_structure_origins",
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
        value_structure_origins:dict[str,"KeymapStructure"],
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
        self.value_structure_origins = value_structure_origins
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

    def get_value_type_use(self, key: Con[K], value: Con[V], usage_tracker:UsageTracker, parent_use:Use|None, trace:Trace, environment:PrinterEnvironment) -> TypeUse:
        string_key = self.key_function(key.data)
        for value_type in self.value_types[string_key]:
            if isinstance(value.data, value_type):
                return TypeUse(value_type, Region.value_types, KeyUse(string_key, self.value_structure_origins[string_key], None, NonEmptyUse(self, None, StructureUse(self, None, parent_use))), usage_tracker)
        else: raise StructureTypeError(self.value_types[string_key], type(value.data), "Value")

    def always_empty(self) -> bool:
        return len(self.value_structures) == 0

    def get_key_value_parent_use(self, key: Con[K], value: Con[V], non_empty_use: NonEmptyUse) -> Use:
        string_key = self.key_function(key.data)
        return KeyUse(string_key, self.value_structure_origins[string_key], None, non_empty_use)

    def get_uses(self, data: ICon[Con[K], Con[V], D], usage_tracker:UsageTracker, parent_use:Use|None, trace: Trace, environment: PrinterEnvironment) -> OrderedSet[Use]:
        if not usage_tracker.still_used(self): return OrderedSet(())
        with trace.enter(self, self.trace_name, data):
            output:OrderedSet[Use] = OrderedSet(())
            output.update(super().get_uses(data, usage_tracker, parent_use, trace, environment))
            non_empty_use = NonEmptyUse(self, None, StructureUse(self, None, parent_use))
            for key, value in data.items():
                with trace.enter_key(key, value):
                    string_key = self.key_function(key.data)
                    origin_structure = self.value_structure_origins[string_key]
                    output.add(KeyUse(string_key, origin_structure, usage_tracker, non_empty_use))
            return output
        return OrderedSet(())

    def get_all_uses(self, memo: set[Structure], parent_use:Use|None) -> OrderedSet[Use]:
        if self in memo: return OrderedSet(())
        output:OrderedSet[Use] = OrderedSet(())
        output.update(super().get_all_uses(memo, parent_use))
        non_empty_use = NonEmptyUse(self, None, StructureUse(self, None, parent_use))
        if self.key_structure is not None:
            output.update(self.key_structure.get_all_uses(memo, non_empty_use if self.key_structure.is_inline else None))
        for (string_key, value_structure), (string_key, value_types) in zip(self.value_structures.items(), self.value_types.items(), strict=True):
            origin_structure = self.value_structure_origins[string_key]
            key_use = KeyUse(string_key, origin_structure, None, non_empty_use)
            output.add(key_use)
            if value_structure is not None:
                output.update(value_structure.get_all_uses(memo, non_empty_use if value_structure.is_inline else None))
            for value_type in value_types:
                output.add(TypeUse(value_type, Region.value_types, key_use, None))
        return output

    def get_value_types(self, key: K, value: V, trace: Trace, environment: PrinterEnvironment) -> tuple[type, ...]:
        if (output := self.value_types.get(self.key_function(key), ...)) is ...:
            trace.exception(StructureUnrecognizedKeyError(key))
            return (object,) # catches everything. Ensures that additional, unnecessary errors don't occur.
        return output

    def get_value_tags(self, key: K, value: V, trace: Trace, environment: PrinterEnvironment) -> set[StructureTag]|None:
        return self.value_tags.get(self.key_function(key))

    def allow_key_move(self, key1: Con[K], key2: Con[K], value1: Con[V], value2: Con[V], branch1: int, branch2: int, trace: Trace, environment: ComparisonEnvironment) -> bool:
        # Returns True if the values and keys share a common Structure
        if not self.allow_key_moves: return False
        value_structure1 = self.get_value_structure(key1.data, value1.data, trace, environment[branch1])
        if value_structure1 is None: return False
        value_structure2 = self.get_value_structure(key2.data, value2.data, trace, environment[branch1])
        if value_structure2 is not value_structure1: return False

        key_structure1 = self.get_key_structure(key1.data, value1.data, trace, environment[branch1])
        if key_structure1 is None: return False
        key_structure2 = self.get_key_structure(key2.data, value2.data, trace, environment[branch1])
        if key_structure2 is not key_structure1: return False

        return True

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
