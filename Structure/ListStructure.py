from typing import Sequence, cast

import Structure.AbstractIterableStructure as AbstractIterableStructure
import Structure.Difference as D
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions


class ListStructure[d](AbstractIterableStructure.AbstractIterableStructure[d]):
    """
    Ordered data structure.
    """

    def get_similarity(self, data1: Sequence[d|D.Diff[d]], data2: Sequence[d], depth:int, max_depth:int|None, environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace], branch:int) -> float:
        if (max_depth is not None and depth > max_depth) or (self.max_similarity_ancestor_depth is not None and depth > self.max_similarity_ancestor_depth):
            if branch == 0:
                return float(data1 == data2)
            else:
                return float(Structure.get_data_at_branch(data1, branch) == data2)
        maximum_length = max(len(data1), len(data2))
        if self.structure is None:
            similarity = sum(D.last_value(item1) == item2 for item1, item2 in zip(data1, data2)) / maximum_length
        else:
            similarity = sum(self.structure.get_similarity(D.last_value(item1), item2, depth + 1, max_depth, environment, exceptions, branch) for item1, item2 in zip(data1, data2)) / maximum_length
        if similarity < 0.0 or similarity > 1.0:
            exceptions.append(Trace.ErrorTrace(Exceptions.InvalidSimilarityError(self, similarity, data1, data2), self.name, None, (data1, data2)))
        return similarity

    def compare(
        self,
        data1:Sequence[d|D.Diff[d]],
        data2:Sequence[d],
        environment:StructureEnvironment.ComparisonEnvironment,
        branch:int,
        branches:int,
    ) -> tuple[Sequence[d|D.Diff[d]],bool,list[Trace.ErrorTrace]]:
        if not environment.is_multi_diff and (data1 is data2 or data1 == data2):
            return data1, False, []
        has_changes = False
        exceptions:list[Trace.ErrorTrace] = []

        output:list[d|D.Diff[d]] = []
        index = -1 # this exists because `index` is used after the for loop and would be unbound if this statement wasn't here.
        for index, (item1, item2) in enumerate(zip(data1, data2)):
            if item1 is item2 or item1 == item2:
                compare_output = item1
            elif self.structure is None:
                has_changes = True
                if isinstance(item1, D.Diff):
                    item1_diff = cast("D.Diff[d]", item1)
                    if item1_diff.last_value == item2:
                        compare_output = item1.extend(branch+1)
                    else:
                        compare_output = item1.append(branch+1, item2)
                else:
                    item1_object = cast(d, item1)
                    compare_output = D.Diff(branches, {tuple(range(0,branch+1)): item1_object, (branch+1,): item2})
            elif isinstance(item1, D.Diff):
                has_changes = True
                item1_diff = cast("D.Diff[d]", item1)
                comparison, _, new_exceptions = self.structure.compare(item1_diff.last_value, item2, environment, branch, branches)
                exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
                compare_output = item1_diff.with_last_as(branch+1, comparison)
            else:
                item1_object = cast(d, item1)
                compare_output, subcomponent_has_changes, new_exceptions = self.structure.compare(item1_object, item2, environment, branch, branches)
                exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
                has_changes = has_changes or subcomponent_has_changes
            output.append(compare_output)
        # now, only the shortest iterable has been consumed.
        if len(data1) != len(data2):
            if len(data1) > len(data2):
                iterator = data1[index + 1:]
                inequal_size_branches = tuple(range(0,branch+1))
            else:
                iterator = data2[index + 1:]
                inequal_size_branches = (branch + 1,)
            for item in iterator:
                if isinstance(item, D.Diff):
                    output.append(item) # the only time item can be a Diff is when the item is being removed.
                    # In that case, it does not need to be modified.
                else:
                    output.append(D.Diff(branches, {inequal_size_branches: item}))
            has_changes = True
        else: pass
        output = type(data1)(output) # type: ignore
        return output, has_changes, exceptions
