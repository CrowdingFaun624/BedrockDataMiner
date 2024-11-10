from typing import Sequence, TypeVar

import Structure.AbstractIterableStructure as AbstractIterableStructure
import Structure.Difference as D
import Structure.Hashing as Hashing
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

d = TypeVar("d")

MIN_SIMILARITY_THRESHOLD = 0.5
"""
Float between 0 and 1 describing the fraction of similarity necessary
for an item to be considered "moved" rather than "added" or "removed".
"""

class SetStructure(AbstractIterableStructure.AbstractIterableStructure[d]):
    """
    Unordered data structure.
    """

    def __init__(
        self,
        name: str,
        sort:bool,
        min_similarity_threshold:float,
        children_has_normalizer:bool,
    ) -> None:
        super().__init__(name, children_has_normalizer)

        self.min_similarity_threshold=min_similarity_threshold
        self.sort = sort

    def get_similarity(self, data1:Sequence[d], data2:Sequence[d], environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace]) -> float:
        data1_hashes:dict[int,tuple[int,d]] = {Hashing.hash_data(item): (index, item) for index, item in enumerate(data1)}
        data2_hashes:dict[int,tuple[int,d]] = {Hashing.hash_data(item): (index, item) for index, item in enumerate(data2)}

        same_hashes = data1_hashes.keys() & data2_hashes.keys()
        data1_exclusive_items = {exclusive_hash: data1_hashes[exclusive_hash] for exclusive_hash in data1_hashes.keys() - data2_hashes.keys()}
        data2_exclusive_items = {exclusive_hash: data2_hashes[exclusive_hash] for exclusive_hash in data2_hashes.keys() - data1_hashes.keys()}
        maximum_length = max(len(data1), len(data2))
        similarity = len(same_hashes) / maximum_length
        if self.structure is not None and len(data1_exclusive_items) > 0 and len(data2_exclusive_items) > 0:
            already_data1_hashes:set[int] = set() # items of data1_hashes that have already been picked.
            already_data2_hashes:set[int] = set() # items of data2_hashes that have already been picked.
            for hash1, hash2, item_similarity, _, _ in self.get_similarities_list(data1_exclusive_items, data2_exclusive_items, self.structure, environment, exceptions):
                if hash1 in already_data1_hashes or hash2 in already_data2_hashes:
                    continue
                already_data1_hashes.add(hash1)
                already_data2_hashes.add(hash2)
                similarity += item_similarity / maximum_length
        if similarity < 0.0 or similarity > 1.0:
            exceptions.append(Trace.ErrorTrace(Exceptions.InvalidSimilarityError(self, similarity, data1, data2), self.name, None, (data1, data2)))
        return similarity

    def get_similarities_list(
        self,
        data1_exclusive_items:dict[int,tuple[int,d]],
        data2_exclusive_items:dict[int,tuple[int,d]],
        structure:Structure.Structure[d],
        environment:StructureEnvironment.ComparisonEnvironment,
        exceptions:list[Trace.ErrorTrace],
    ) -> list[tuple[int,int,float,int,int]]:
        similarities_list = [ # maps similarity of older items to newer items
            (hash1, hash2, similarity, index1, index2)
            for hash1, (index1, item1) in data1_exclusive_items.items()
            for hash2, (index2, item2) in data2_exclusive_items.items()
            if (similarity := structure.get_similarity(item1, item2, environment, exceptions)) > self.min_similarity_threshold # similarities less than the threshold don't matter.
        ]
        similarities_list.sort(key=lambda item: (item[2], item[3], item[4]), reverse=True) # sort by similarity; highest similarity is first
        return similarities_list

    def compare(
        self,
        data1:Sequence[d],
        data2:Sequence[d],
        environment:StructureEnvironment.ComparisonEnvironment,
    ) -> tuple[Sequence[d|D.Diff[d|D._NoExistType,d|D._NoExistType]],bool,list[Trace.ErrorTrace]]:
        if data1 is data2 or data1 == data2:
            return data1, False, []
        exceptions:list[Trace.ErrorTrace] = []

        data1_hashes:dict[int,tuple[int,d]] = {Hashing.hash_data(item): (index, item) for index, item in enumerate(data1)}
        data2_hashes:dict[int,tuple[int,d]] = {Hashing.hash_data(item): (index, item) for index, item in enumerate(data2)}

        same_hashes = [hash for hash in data1_hashes.keys() if hash in data2_hashes] # retain order
        data1_exclusive_items = {exclusive_hash: data1_hashes[exclusive_hash] for exclusive_hash in data1_hashes if exclusive_hash not in data2_hashes}
        data2_exclusive_items = {exclusive_hash: data2_hashes[exclusive_hash] for exclusive_hash in data2_hashes if exclusive_hash not in data1_hashes}
        output:list[d|D.Diff[d|D.NoExist,d|D.NoExist]] = type(data1)() # type: ignore
        has_changes = len(data1_exclusive_items) > 0 or len(data2_exclusive_items) > 0

        # unchanged items
        for same_hash in same_hashes:
            output.append(data1_hashes[same_hash][1])

        # changed items
        already_data1_hashes:set[int] = set() # items of data1_hashes that have already been picked.
        already_data2_hashes:set[int] = set() # items of data2_hashes that have already been picked.
        # if there is no structure, there's no similarity between items so the change step can be skipped.
        if self.structure is not None and len(data1_exclusive_items) > 0 and len(data2_exclusive_items) > 0:
            for hash1, hash2, _, _, _ in self.get_similarities_list(data1_exclusive_items, data2_exclusive_items, self.structure, environment, exceptions):
                if hash1 in already_data1_hashes or hash2 in already_data2_hashes:
                    continue # if either side is already involved in a change, it's unneeded.
                already_data1_hashes.add(hash1)
                already_data2_hashes.add(hash2)
                compare_output, _, new_exceptions = self.structure.compare(data1_exclusive_items[hash1][1], data2_exclusive_items[hash2][1], environment)
                exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
                output.append(compare_output)

        # added/removed items
        output.extend(
            D.Diff(old=item)
            for exclusive_hash, (index, item) in data1_exclusive_items.items()
            if exclusive_hash not in already_data1_hashes
        )
        output.extend(
            D.Diff(new=item)
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
