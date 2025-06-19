from collections import defaultdict
from enum import Enum
from typing import TYPE_CHECKING, Container, Iterable, Sequence

import Domain.Domain as Domain

if TYPE_CHECKING:
    from Structure.IterableStructure import IterableStructure
    from Structure.Structure import Structure
    from Structure.StructureBase import StructureBase
    from Structure.StructureTypes.ConditionStructure import ConditionStructure
    from Structure.StructureTypes.KeymapStructure import KeymapStructure
    from Structure.StructureTypes.SwitchStructure import SwitchStructure
    from Structure.StructureTypes.UnionStructure import UnionStructure


class Region(Enum):
    this_types = 0
    key_types = 1
    value_types = 2 # grr cannot use `value`

class Use(): # pronounced like the noun use, YOOS

    __slots__ = (
        "domain",
        "hash",
        "origin",
        "parent",
    )

    def __init__(self, origin:"Structure", usage_tracker:"UsageTracker|None", parent:"Use|None"=None) -> None:
        self.origin = origin
        self.parent = parent # this Use will only show if `parent` is not unused.
        self.hash = self.get_hash()
        self.domain:Domain.Domain|None = None if usage_tracker is None else usage_tracker.domain
        if usage_tracker is not None:
            usage_tracker.report_use(self)

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Use)

    def get_hash(self) -> int:
        ...

    def __hash__(self) -> int:
        return self.hash

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id {id(self)}>"

    def message(self) -> str:
        '''
        The message given if this Use is unused.
        '''
        ...

    def name(self) -> str:
        '''
        A short string of this Use. Used in TypeUse only.
        '''
        ...

    def should_display(self, unused:Container["Use"]) -> bool:
        return self.parent is None or self.parent not in unused
        # return self in unused and (self.parent is None or not self.parent.should_display(unused))

class StructureUse[T:"Structure"](Use):

    __slots__ = (
        "structure",
    )

    def __init__(self, structure:T, usage_tracker:"UsageTracker|None", parent:Use|None, ) -> None:
        self.structure:T = structure
        super().__init__(structure, usage_tracker, parent)

    def __hash__(self) -> int:
        return self.hash

    def __eq__(self, value: object) -> bool:
        return isinstance(value, StructureUse) and self.structure == value.structure

    def get_hash(self) -> int:
        return hash((self.structure, type(self)))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.structure.full_name}>"

    def message(self) -> str:
        return f"Structure {self.structure.full_name} is not used."

    def name(self) -> str:
        return self.structure.full_name

class TypeUse(Use):

    __slots__ = (
        "region",
        "subuse",
        "use_type",
    )

    def __init__(self, use_type:type, region:Region, subuse:Use, usage_tracker:"UsageTracker|None") -> None:
        self.use_type = use_type
        self.region = region
        self.subuse = subuse
        super().__init__(subuse.origin, usage_tracker, subuse)

    def __hash__(self) -> int:
        return self.hash

    def __eq__(self, value: object) -> bool:
        return isinstance(value, TypeUse) and self.use_type == value.use_type and self.region == value.region and self.subuse == value.subuse

    def get_hash(self) -> int:
        return hash((self.use_type, self.subuse, self.region, type(self)))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.region.name} {self.use_type.__name__} of {self.subuse.name()}>"

    def message(self) -> str:
        region_string = ("\"this\" type", "key type", "value type")[self.region.value]
        type_name = self.domain.type_stuff.type_names.get(self.use_type, self.use_type.__name__) if self.domain is not None else self.use_type.__name__
        return f"The {region_string} \"{type_name}\" of {self.subuse.name()} is not used."

class KeyUse(Use):

    __slots__ = (
        "key",
    )

    def __init__(self, key:str, origin:"KeymapStructure", usage_tracker:"UsageTracker|None", parent:Use|None) -> None:
        self.key:str = key
        super().__init__(origin, usage_tracker, parent)

    def __hash__(self) -> int:
        return self.hash

    def __eq__(self, value: object) -> bool:
        return isinstance(value, KeyUse) and self.key == value.key and self.origin == value.origin

    def get_hash(self) -> int:
        return hash((self.key, self.origin, type(self)))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.key} of {self.origin.full_name}>"

    def message(self) -> str:
        return f"The key \"{self.key}\" of {self.origin.full_name} is not used."

    def name(self) -> str:
        return f"key \"{self.key}\" of {self.origin.full_name}"

class NonEmptyUse(Use):

    __slots__ = (
        "always_empty",
        "structure",
    )

    def __init__(self, structure:"IterableStructure", usage_tracker:"UsageTracker|None", parent:Use|None, always_empty:bool=False) -> None:
        self.structure = structure
        self.always_empty = always_empty # If True, will not show (I do not simply add it to output because of the Uses that depend on it)
        super().__init__(structure, usage_tracker, parent)

    def __hash__(self) -> int:
        return self.hash

    def __eq__(self, value: object) -> bool:
        return isinstance(value, NonEmptyUse) and self.structure == value.structure

    def get_hash(self) -> int:
        return hash((self.structure, type(self)))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} of {self.structure.full_name}>"

    def message(self) -> str:
        return f"Structure {self.structure.full_name} is always empty."

    def name(self) -> str:
        return self.structure.full_name

    def should_display(self, unused: Container[Use]) -> bool:
        return not self.always_empty and super().should_display(unused)

class ConditionStructureUse(Use):

    __slots__ = (
        "branch",
        "structure",
    )

    def __init__(self, branch:int, structure:"ConditionStructure", usage_tracker:"UsageTracker|None", parent:Use|None, ) -> None:
        self.branch = branch
        self.structure = structure
        super().__init__(structure, usage_tracker, parent)

    def __hash__(self) -> int:
        return self.hash

    def __eq__(self, value: object) -> bool:
        return isinstance(value, ConditionStructureUse) and self.branch == value.branch and self.structure == value.structure

    def get_hash(self) -> int:
        return hash((self.branch, self.structure, type(self)))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.branch} of {self.structure.full_name}>"

    def message(self) -> str:
        return f"The branch {self.branch} of {self.structure.full_name} is unused."

    def name(self) -> str:
        return f"branch {self.branch} of {self.structure.full_name}"

class SwitchStructureUse(Use):

    __slots__ = (
        "structure",
        "switch_key",
    )

    def __init__(self, switch_key:str, structure:"SwitchStructure", usage_tracker:"UsageTracker|None", parent:Use|None, ) -> None:
        self.switch_key = switch_key
        self.structure = structure
        super().__init__(structure, usage_tracker, parent)

    def __hash__(self) -> int:
        return self.hash

    def __eq__(self, value: object) -> bool:
        return isinstance(value, SwitchStructureUse) and self.switch_key == value.switch_key and self.structure == value.structure

    def get_hash(self) -> int:
        return hash((self.switch_key, self.structure, type(self)))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.switch_key} of {self.structure.full_name}>"

    def message(self) -> str:
        return f"The switchkey {self.switch_key} of {self.structure.full_name} is unused."

    def name(self) -> str:
        return f"switchkey {self.switch_key} of {self.structure.full_name}"

class UnionStructureUse(Use):

    __slots__ = (
        "branch_type",
        "structure",
    )

    def __init__(self, branch_type:type, structure:"UnionStructure", usage_tracker:"UsageTracker|None", parent:Use|None, ) -> None:
        self.branch_type = branch_type
        self.structure = structure
        super().__init__(structure, usage_tracker, parent)

    def __hash__(self) -> int:
        return self.hash

    def __eq__(self, value: object) -> bool:
        return isinstance(value, UnionStructureUse) and self.branch_type == value.branch_type and self.structure == value.structure

    def get_hash(self) -> int:
        return hash((self.branch_type, self.structure, type(self)))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.branch_type.__name__} of {self.structure.full_name}>"

    def get_type_name(self) -> str:
        return self.domain.type_stuff.type_names.get(self.branch_type, self.branch_type.__name__) if self.domain is not None else self.branch_type.__name__

    def message(self) -> str:
        return f"The Union-type \"{self.get_type_name()}\" of {self.structure.full_name} is unused."

    def name(self) -> str:
        return f"Union-type \"{self.get_type_name()}\" of {self.structure.full_name}"

class UsageTracker(): # used for optimization without complicated parameters to get_used or attributes of Structures.

    __slots__ = (
        "domain",
        "structure_current_uses",
        "structure_descendants",
        "structure_possible_uses",
        "structure_substructures",
        "structures_with_unused",
        "substructure_structures",
    )

    def __init__(self, start_structures:Sequence["StructureBase"], all_uses:Iterable[Use], domain:"Domain.Domain") -> None:
        all_structures:set["Structure"] = set()
        structure_substructures:dict["Structure", set["Structure"]] = defaultdict(lambda: set())
        substructure_structures:dict["Structure", set["Structure"]] = defaultdict(lambda: set())
        structure_possible_uses:dict["Structure", set[Use]] = defaultdict(lambda: set())
        structure_current_uses:dict["Structure", set[Use]] = defaultdict(lambda: set())
        structure_descendants:dict["StructureBase", set["Structure"]] = {}
        for start_structure in start_structures:
            start_structure.get_descendants(all_structures)
            if start_structure not in structure_descendants:
                structure_descendants[start_structure] = start_structure.get_descendants(set())
                # get_descendants call with empty set is different than with `all_structures`.
        for structure in all_structures:
            for substructure in structure.iter_structures():
                structure_substructures[structure].add(substructure)
                substructure_structures[substructure].add(structure)
            structure_possible_uses[structure] = set()
            structure_current_uses[structure] = set()
        for use in all_uses:
            structure_possible_uses[use.origin].add(use)

        self.structures_with_unused = all_structures
        self.structure_substructures = structure_substructures
        self.substructure_structures = substructure_structures
        self.structure_possible_uses = structure_possible_uses
        self.structure_current_uses = structure_current_uses
        self.structure_descendants = structure_descendants
        self.domain = domain

    def report_use(self, use:Use) -> None:
        '''
        Called by a Use when created.
        '''
        self.structure_current_uses[use.origin].add(use)
        self.still_used(use.origin) # There is the potential that `still_used` won't be called again, so this must be called to make sure everything ends up used if it should be.

    def still_used(self, structure:"Structure") -> bool:
        if structure not in self.structures_with_unused or len(self.structure_substructures[structure]) > 0:
            return True
        elif len(self.structure_current_uses[structure]) >= len(self.structure_possible_uses[structure]) and len(self.structure_substructures[structure]) == 0:
            self.mark_as_used(structure)
            return False
        else:
            return True

    def mark_as_used(self, structure:"Structure") -> None:
        for superstructure in self.substructure_structures[structure]: # all structures with `structure` as a child
            self.structure_substructures[superstructure].remove(structure)
            if len(self.structure_current_uses[superstructure]) >= len(self.structure_possible_uses[superstructure]) and len(self.structure_substructures[superstructure]) == 0 and superstructure in self.structures_with_unused:
                self.mark_as_used(superstructure)
        self.structures_with_unused.discard(structure) # placed last because of potential looping problems.

    def everything_used(self, structure_bases:Iterable["StructureBase"]) -> bool:
        return all(structure not in self.structures_with_unused for structure_base in structure_bases for structure in self.structure_descendants[structure_base])

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.domain.name}>"

# entities has 1048 out of 8125
