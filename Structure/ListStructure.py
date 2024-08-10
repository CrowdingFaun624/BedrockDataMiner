from typing import Sequence, TypeVar, cast

import Structure.AbstractIterableStructure as AbstractIterableStructure
import Structure.Difference as D
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

d = TypeVar("d")

class ListStructure(AbstractIterableStructure.AbstractIterableStructure[d]):
    """
    Ordered data structure.
    """

    def get_similarity(self, data1: Sequence[d], data2: Sequence[d], environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace]) -> float:
        maximum_length = max(len(data1), len(data2))
        if self.structure is None:
            similarity = sum(item1 == item2 for item1, item2 in zip(data1, data2)) / maximum_length
        else:
            similarity = sum(self.structure.get_similarity(item1, item2, environment, exceptions) for item1, item2 in zip(data1, data2)) / maximum_length
        if similarity < 0.0 or similarity > 1.0:
            exceptions.append(Trace.ErrorTrace(Exceptions.InvalidSimilarityError(self, similarity, data1, data2), self.name, None, (data1, data2)))
        return similarity

    def compare(
        self,
        data1:Sequence[d],
        data2:Sequence[d],
        environment:StructureEnvironment.ComparisonEnvironment,
    ) -> tuple[Sequence[d|D.Diff[D._NoExistType,d]|D.Diff[d,D._NoExistType]],bool,list[Trace.ErrorTrace]]:
        if data1 is data2 or data1 == data2:
            return data1, False, []
        has_changes = False
        exceptions:list[Trace.ErrorTrace] = []

        output:list[d|D.Diff[D._NoExistType,d]|D.Diff[d,D._NoExistType]] = []
        exceptions:list[Trace.ErrorTrace] = []
        index = -1
        for index, (item1, item2) in enumerate(zip(data1, data2)):
            # type exception handling
            if (check_type_exception := self.check_type(index, item1)) is not None:
                exceptions.append(check_type_exception)
            if (check_type_exception := self.check_type(index, item2)) is not None:
                exceptions.append(check_type_exception)

            if item1 == item2:
                output.append(item1)
            else:
                if self.structure is None:
                    compare_output = D.Diff(item1, item2)
                    has_changes = True
                else:
                    compare_output, subcomponent_has_changes, new_exceptions = self.structure.compare(item1, item2, environment)
                    has_changes = has_changes or subcomponent_has_changes
                    exceptions.extend(exception.add(self.name, index) for exception in new_exceptions)
                output.append(cast(d, compare_output))
        # now, only the shortest iterable has been consumed.
        if len(data1) != len(data2):
            if len(data1) > len(data2):
                iterator = data1[index + 1:] # pls don't break
                data1_is_bigger = True
            else:
                iterator = data2[index + 1:]
                data1_is_bigger = False
            for i, item in enumerate(iterator):
                # index is end of shortest; i is the offset from that.
                if (check_type_exception := self.check_type(index + i + 1, item)) is not None:
                    exceptions.append(check_type_exception)
                output.append(D.Diff(old=item) if data1_is_bigger else D.Diff(new=item))
                has_changes = True
        else: pass
        output = type(data1)(output) # type: ignore
        return output, has_changes, exceptions

    def get_item_key(self, index:int) -> str:
        return " %i" % (index,)

    def get_compare_text_key_str(self, index:int) -> str|int|None:
        return index
