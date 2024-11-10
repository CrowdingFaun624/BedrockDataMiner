import Structure.Difference as D
import Structure.PrimitiveStructure as PrimitiveStructure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions


class StringStructure(PrimitiveStructure.PrimitiveStructure[str]):

    def get_levenshtein_distance(self, data1:str, data2:str) -> int:
        distances:list[list[int]] = [[0] * (len(data1) + 1) for y in range(len(data2) + 1)]
        for x in range(1, len(data1) + 1):
            distances[0][x] = x
        for y in range(1, len(data2) + 1):
            distances[y][0] = y
        for y in range(len(data2)):
            for x in range(len(data1)):
                distances[y + 1][x + 1] = min(
                    distances[y+1][x] + 1,
                    distances[y][x+1] + 1,
                    distances[y][x] + int(data1[x] != data2[y]),
                )
        return distances[len(data2)][len(data1)]

    def get_similarity(self, data1: str, data2: str, environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace]) -> float:
        if len(data1) * len(data2) > 1_000_000:
            raise Exceptions.SequenceTooLongError(self, len(data1), len(data2))
        if len(data1) == 0 and len(data2) == 0:
            return 1.0
        max_length = len(data1) if len(data1) > len(data2) else len(data2)
        levenshtein_distance = self.get_levenshtein_distance(data1, data2)
        return 1 - (levenshtein_distance / max_length)

    def compare(self, data1: str, data2: str, environment: StructureEnvironment.ComparisonEnvironment) -> tuple[str|D.Diff[str,str], bool, list[Trace.ErrorTrace]]:
        if data1 is data2 or data1 == data2:
            return data1, False, []
        else:
            return D.Diff(old=data1, new=data2), True, []
