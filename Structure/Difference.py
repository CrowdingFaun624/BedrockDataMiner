from types import EllipsisType
from typing import Hashable, Mapping

from Structure.Container import Don


class Diff[A: Don]():
    '''
    Object that tracks potential differences.
    '''

    __slots__ = (
        "branch_count",
        "bundles",
        "contains_diffs",
        "hash",
        "items",
    )

    def __init__(self, items:Mapping[tuple[int, ...], A], contains_diffs:bool) -> None:
        '''
        :items: The non-empty dictionary (sorted by first branch of each
        bundle) of (bundle that has this item) to (value at that bundle). All
        branches from 0 to N should be present.
        :contains_diffs: If any value in `items` is or contains a Diff with a `length` greater than 1.
        Should not be true if only self has a length greater than 1.
        '''
        self.contains_diffs:bool = contains_diffs
        '''
        If any value in `items` is or contains a Diff that has a difference or is missing a branch from all possible branches.
        '''
        self.items:Mapping[tuple[int,...], A] = items
        '''
        The dictionary (sorted by first branch of each bundle) of (bundle that
        has this item) to (value at that bundle).
        '''
        self.branch_count:int = 0
        '''
        The total number of branches that this Diff tracks. Equal to the last
        branch + 1.
        '''
        self.bundles:list[tuple[int,...]]
        '''
        A mapping from branch to the bundle it is in. If the branch does not exist in this Diff, its index will be an empty tuple.
        '''

        hashable_material:list[Hashable] = [0] * (len(items) * 2)
        for index, (bundle, value) in enumerate(items.items()):
            hashable_material[index * 2] = value
            hashable_material[index * 2 + 1] = bundle
            self.branch_count = bundle[-1] + 1
        self.hash = hash(tuple(hashable_material))
        self.bundles = [()] * self.branch_count
        for bundle in items.keys():
            for branch in bundle:
                self.bundles[branch] = bundle

    def __repr__(self) -> str:
        return f"<Diff {" → ".join(f"{item} at {index[0] if len(index) == 1 else index}" for index, item in self.items.items())}>"

    @property
    def last_value(self) -> A:
        return self[self.branch_count - 1]

    @property
    def length(self) -> int:
        '''
        The total number of bundles that this Diff tracks.
        '''
        return len(self.items)

    # TODO: make it actually raise errors as described.
    def __getitem__(self, index:int|tuple[int,...]) -> A:
        '''
        Gets the item at the given index. If it is not present due to
        out-of-bounds, raises an IndexError. If it is not present due to a
        malformed bundle, raises a KeyError. If it is not present due to not
        existing, raises a DiffKeyError.
        :index: The branch or bundle.
        '''
        return self.items[self.bundles[index] if isinstance(index, int) else index]

    def __contains__(self, index:int|tuple[int,...]) -> bool:
        '''
        Returns if the index is in-bounds. Will return True even if there is no
        existing value at that index.
        :index: The branch or bundle.
        '''
        return (index >= 0 and index < self.branch_count) if isinstance(index, int) else index in self.items

    def value_exists_at(self, index:int|tuple[int,...]) -> bool:
        '''
        Returns if the index is in-bounds an a value exists at that index.
        :index: The branch or bundle.
        '''
        return (index >= 0 and index < self.branch_count and len(self.bundles[index]) != 0) if isinstance(index, int) else index in self.items

    def get(self, index:int|tuple[int,...]) -> A|EllipsisType:
        '''
        Gets the item at the given index. If it is not present due to not
        existing, returns an Ellipsis object.. If it is not present due to
        out-of-bounds, raises an IndexError. If it is not present due to a
        malformed bundle, raises a KeyError.
        :index: The branch or bundle.
        :default: The default value to return if there is no existing value at
        `index`. Defaults to Ellipsis.
        '''
        bundle = self.bundles[index] if isinstance(index, int) else index
        if len(bundle) == 0:
            return ...
        return self.items.get(bundle, ...)

    def __hash__(self) -> int:
        return self.hash

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Diff):
            return self.contains_diffs == value.contains_diffs and self.items == value.items
        return False
