from typing import TYPE_CHECKING, Sequence, cast

import Structure.AbstractIterableStructure as AbstractIterableStructure
import Structure.Difference as D
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

MIN_SIMILARITY_THRESHOLD = 0.5
"""
Float between 0 and 1 describing the fraction of similarity necessary
for an item to be considered "moved" rather than "added" or "removed".
"""

class SetStructure[d](AbstractIterableStructure.AbstractIterableStructure[d]):
    """
    Unordered data structure.
    """

    __slots__ = (
        "min_similarity_threshold",
        "sort",
    )

    def __init__(
        self,
        name: str,
        sort:bool,
        min_similarity_threshold:float,
        max_similarity_descendent_depth:int|None,
        max_similarity_ancestor_depth:int|None,
        children_has_normalizer:bool,
        children_has_garbage_collection:bool,
    ) -> None:
        super().__init__(name, max_similarity_descendent_depth, max_similarity_ancestor_depth, children_has_normalizer, children_has_garbage_collection)

        self.min_similarity_threshold=min_similarity_threshold
        self.sort = sort

    def get_similarity(self, data1:Sequence[d], data2:Sequence[d], depth:int, max_depth:int|None, environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace], branch:int) -> float:
        if (max_depth is not None and depth > max_depth) or (self.max_similarity_ancestor_depth is not None and depth > self.max_similarity_ancestor_depth):
            if branch == 0:
                return float(data1 == data2)
            else:
                return float(Structure.get_data_at_branch(data1, branch) == data2)

        type_stuff = environment.domain.type_stuff
        data1_hashes:dict[int,tuple[int,d|D.Diff[d]]] = {type_stuff.hash_data(item): (index, item) for index, item in enumerate(data1)}
        data2_hashes:dict[int,tuple[int,d]] = {type_stuff.hash_data(item): (index, item) for index, item in enumerate(data2)}

        same_hashes = data1_hashes.keys() & data2_hashes.keys()
        data1_exclusive_items = {exclusive_hash: data1_hashes[exclusive_hash] for exclusive_hash in data1_hashes.keys() - data2_hashes.keys()}
        data2_exclusive_items = {exclusive_hash: data2_hashes[exclusive_hash] for exclusive_hash in data2_hashes.keys() - data1_hashes.keys()}
        maximum_length = max(len(data1), len(data2))
        similarity = len(same_hashes) / maximum_length
        if self.structure is not None and len(data1_exclusive_items) > 0 and len(data2_exclusive_items) > 0:
            already_data1_hashes:set[int] = set() # items of data1_hashes that have already been picked.
            already_data2_hashes:set[int] = set() # items of data2_hashes that have already been picked.
            for hash1, hash2, item_similarity, _, _ in self.get_similarities_list(data1_exclusive_items, data2_exclusive_items, self.structure, depth, max_depth, environment, exceptions, branch):
                if hash1 in already_data1_hashes or hash2 in already_data2_hashes:
                    if len(already_data1_hashes) == len(data1_exclusive_items) or len(already_data2_hashes) == len(data2_exclusive_items):
                        break
                    continue
                already_data1_hashes.add(hash1)
                already_data2_hashes.add(hash2)
                similarity += item_similarity / maximum_length
        if similarity < 0.0 or similarity > 1.0:
            exceptions.append(Trace.ErrorTrace(Exceptions.InvalidSimilarityError(self, similarity, data1, data2), self.name, None, (data1, data2)))
        return similarity

    def get_similarities_list(
        self,
        data1_exclusive_items:dict[int,tuple[int,d|D.Diff[d]]],
        data2_exclusive_items:dict[int,tuple[int,d]],
        structure:Structure.Structure[d],
        depth:int,
        max_depth:int|None,
        environment:StructureEnvironment.ComparisonEnvironment,
        exceptions:list[Trace.ErrorTrace],
        branch:int,
    ) -> list[tuple[int,int,float,int,int]]:
        similarities_list = [ # maps similarity of older items to newer items
            (hash1, hash2, similarity, index1, index2)
            for hash1, (index1, item1) in data1_exclusive_items.items()
            for hash2, (index2, item2) in data2_exclusive_items.items()
            if (similarity := structure.get_similarity(D.last_value(item1), item2, depth + 1, max_depth, environment, exceptions, branch)) > self.min_similarity_threshold # similarities less than the threshold don't matter.
        ]
        similarities_list.sort(key=lambda item: (item[2], item[3], item[4]), reverse=True) # sort by similarity; highest similarity is first
        return similarities_list

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
        exceptions:list[Trace.ErrorTrace] = []

        type_stuff = environment.domain.type_stuff
        data1_hashes:dict[int,tuple[int,d|D.Diff[d]]] = {type_stuff.hash_data(D.last_value(item)): (index, item) for index, item in enumerate(data1)}
        data2_hashes:dict[int,tuple[int,d]] = {type_stuff.hash_data(item): (index, item) for index, item in enumerate(data2)}

        same_hashes = [hash for hash in data1_hashes.keys() if hash in data2_hashes] # retain order
        data1_exclusive_items = {exclusive_hash: data1_hashes[exclusive_hash] for exclusive_hash in data1_hashes if exclusive_hash not in data2_hashes}
        data2_exclusive_items = {exclusive_hash: data2_hashes[exclusive_hash] for exclusive_hash in data2_hashes if exclusive_hash not in data1_hashes}
        output:list[d|D.Diff[d]] = type(data1)() # type: ignore
        has_changes = len(data1_exclusive_items) > 0 or len(data2_exclusive_items) > 0

        # unchanged items
        # or, more specifically, items that are unchanged between branch and branch+1
        for same_hash in same_hashes:
            item = data1_hashes[same_hash][1]
            if isinstance(item, D.Diff):
                item_diff = cast("D.Diff[d]", item)
                item = item_diff.extend(branch+1)
            elif TYPE_CHECKING:
                item = cast(d, item)
            output.append(item)

        # changed items
        already_data1_hashes:set[int] = set() # items of data1_hashes that have already been picked.
        already_data2_hashes:set[int] = set() # items of data2_hashes that have already been picked.
        # if there is no structure, there's no similarity between items so the change step can be skipped.
        if self.structure is not None and len(data1_exclusive_items) > 0 and len(data2_exclusive_items) > 0:
            for hash1, hash2, _, _, _ in self.get_similarities_list(data1_exclusive_items, data2_exclusive_items, self.structure, 1, self.max_similarity_descendent_depth, environment, exceptions, branch):
                if hash1 in already_data1_hashes or hash2 in already_data2_hashes:
                    if len(already_data1_hashes) == len(data1_exclusive_items) or len(already_data2_hashes) == len(data2_exclusive_items):
                        break
                    continue # if either side is already involved in a change, it's unneeded.
                already_data1_hashes.add(hash1)
                already_data2_hashes.add(hash2)
                index1, item1 = data1_exclusive_items[hash1]
                index2, item2 = data2_exclusive_items[hash2]
                # print(item2)
                if item1 is item2 or item1 == item2:
                    compare_output = item1
                elif self.structure is None:
                    if isinstance(item1, D.Diff):
                        item1_diff = cast("D.Diff[d]", item1)
                        if item1.last_value == item2:
                            compare_output = item1_diff.extend(branch+1)
                        else:
                            compare_output = item1_diff.append(branch+1, item2)
                    else:
                        item1_object = cast(d, item1)
                        compare_output = D.Diff(branches, {tuple(range(0,branch+1)): item1_object, (branch+1,): item2})
                elif isinstance(item1, D.Diff):
                    item1_diff = cast("D.Diff[d]", item1)
                    comparison, _, new_exceptions = self.structure.compare(item1_diff.last_value, item2, environment, branch, branches)
                    exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
                    compare_output = item1_diff.with_last_as(branch+1, comparison)
                else:
                    item1_object = cast(d, item1)
                    compare_output, _, new_exceptions = self.structure.compare(item1_object, item2, environment, branch, branches)
                    exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
                output.append(compare_output)

        # removed items
        output.extend(
            item if isinstance(item, D.Diff) else D.Diff(branches, {tuple(range(0,branch+1)): item})
            for exclusive_hash, (index, item) in data1_exclusive_items.items()
            if exclusive_hash not in already_data1_hashes
        )
        # added items
        output.extend(
            D.Diff(branches, {(branch+1,): item})
            for exclusive_hash, (index, item) in data2_exclusive_items.items()
            if exclusive_hash not in already_data2_hashes
        )

        if self.sort:
            output.sort() # type: ignore
        return output, has_changes, exceptions

    def get_item_key(self, index: int) -> str:
        return ""

    def get_compare_text_key_str(self, index:int) -> str|int|None:
        return None
