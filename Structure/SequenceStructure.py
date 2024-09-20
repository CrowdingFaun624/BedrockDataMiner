import enum
from typing import Sequence, TypeVar

import Structure.AbstractIterableStructure as AbstractIterableStructure
import Structure.Difference as D
import Structure.Hashing as Hashing
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

d = TypeVar("d")

class Direction(enum.Enum):
    '''
    Utility class used to retrace the most efficient path given
    by the Levenshtein algorithm.
    '''
    none = "."
    "value not filled in/top left of edit matrix"
    horizontal = ">"
    "deletion"
    vertical = "v"
    "addition"
    diagonal_substitution = "\\"
    "substitution"
    diagonal_no_change = "-"
    "no change"

class SequenceStructure(AbstractIterableStructure.AbstractIterableStructure[d]):
    '''
    Sequential data structure. Uses levenshtein distance for comparing.
    '''

    def __init__(self, name: str, addition_cost:float, deletion_cost:float, substitution_cost:float, children_has_normalizer: bool, children_tags: set[str]) -> None:
        super().__init__(name, children_has_normalizer, children_tags)

        self.addition_cost = addition_cost
        self.deletion_cost = deletion_cost
        self.substitution_cost = substitution_cost

    def get_similarity(self, data1: Sequence[d], data2: Sequence[d], environment: StructureEnvironment.ComparisonEnvironment, exceptions: list[Trace.ErrorTrace]) -> float:
        pass
        if self.structure is None:
            raise Exceptions.AttributeNoneError("structure", self)
        distances:list[list[float]] = [[0] * (len(data1) + 1) for y in range(len(data2) + 1)]
        for x in range(1, len(data1) + 1):
            distances[0][x] = x
        for y in range(1, len(data2) + 1):
            distances[y][0] = y
        for y in range(len(data2)):
            for x in range(len(data1)):
                distances[y + 1][x + 1] = min(
                    distances[y + 1][x] + 1,
                    distances[y][x + 1] + 1,
                    distances[y][x] + self.structure.get_similarity(data1[x], data2[y], environment, exceptions),
                )
        levenshtein_distance = distances[len(data2)][len(data1)]
        max_length = len(data1) if len(data1) > len(data2) else len(data2)
        return 1 - (levenshtein_distance / max_length)

    def compare(
        self,
        data1:Sequence[d],
        data2:Sequence[d],
        environment:StructureEnvironment.ComparisonEnvironment,
    ) -> tuple[Sequence[d|D.Diff], bool, list[Trace.ErrorTrace]]:
        if data1 is data2 or data1 == data2:
            return data1, False, []
        exceptions:list[Trace.ErrorTrace] = []
        if self.structure is None:
            raise Exceptions.AttributeNoneError("structure", self)

        data1_hashes:list[int] = [Hashing.hash_data(item) for item in data1]
        data2_hashes:list[int] = [Hashing.hash_data(item) for item in data2]
        distances:list[list[float]] = [[0] * (len(data1) + 1) for y in range(len(data2) + 1)]
        path:list[list[Direction]] = [[Direction.none] * (len(data1) + 1) for y in range(len(data2) + 1)]
        for x in range(1, len(data1) + 1):
            distances[0][x] = x
            path[0][x] = Direction.horizontal
        for y in range(1, len(data2) + 1):
            distances[y][0] = y
            path[y][0] = Direction.vertical
        for y in range(len(data2)):
            for x in range(len(data1)):
                deletion_cost = distances[y + 1][x] + self.deletion_cost
                addition_cost = distances[y][x + 1] + self.addition_cost
                if data1_hashes[x] == data2_hashes[y]:
                    substitution_cost = 0
                    substitution_direction = Direction.diagonal_no_change
                else:
                    substitution_cost = (1 - self.structure.get_similarity(data1[x], data2[y], environment, exceptions)) * self.substitution_cost
                    substitution_direction = Direction.diagonal_substitution
                if substitution_cost < addition_cost and substitution_cost < deletion_cost:
                    cost = substitution_cost
                    direction = substitution_direction
                elif addition_cost < substitution_cost and addition_cost < deletion_cost:
                    cost = addition_cost
                    direction = Direction.vertical
                else:
                    cost = deletion_cost
                    direction = Direction.horizontal
                path[y + 1][x + 1] = direction
                distances[y + 1][x + 1] = cost

        # retrace steps
        has_changes = False
        output:list[d|D.Diff] = []
        x = len(data1) # x and y represent (at first) the bottom right corner of an edit distance matrix.
        y = len(data2)
        while x != 0 or y != 0:
            match path[y][x]:
                case Direction.diagonal_no_change:
                    x -= 1; y -= 1
                    output.append(data1[x]) # data1[x] and data2[y] must be equal
                case Direction.diagonal_substitution:
                    has_changes = True
                    x -= 1; y -= 1
                    comparison, any_changes, new_exceptions = self.structure.compare(data1[x], data2[y], environment)
                    has_changes = has_changes or any_changes
                    exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
                    output.append(comparison)
                case Direction.vertical:
                    has_changes = True
                    y -= 1
                    output.append(D.Diff(new=data2[y]))
                case Direction.horizontal:
                    has_changes = True
                    x -= 1
                    output.append(D.Diff(old=data1[x]))
                case Direction.none:
                    raise Exceptions.InvalidStateError("Direction.none in middle of table!")
        output.reverse() # the above process starts at the end of the sequence and goes backward
        
        if type(data1) == list:
            actual_output:Sequence[d|D.Diff] = output
        else:
            # like, what's the point of having a MutableSequence type if it
            # just doesn't work? If I try using it in this function then it
            # will just act like a normal list without the special features
            # that Sequence has. It's really pissing me off and it's why I'm
            # doing weird stuff like this.
            actual_output = type(data1)(output) # type: ignore
        return actual_output, has_changes, exceptions
