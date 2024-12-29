from typing import Any, Iterable, NoReturn, cast

import Component.Types as Types
import Utilities.Exceptions as Exceptions


@Types.register_decorator(None, hashing_method=hash)
class _NoExistType():
    "Class that is different from None."

    def __hash__(self) -> int:
        return hash(None)

    def __str__(self) -> NoReturn:
        raise Exceptions.CannotStringifyError(type(self))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

NoExist = _NoExistType()

@Types.register_decorator(None, hashing_method=lambda data: hash(tuple(Types.hash_data(item) for item in cast(Diff, data).items.items())))
class Diff[Dt1]():
    '''
    An immutable object containing a difference in data from version to version.
    '''

    __slots__ = (
        "branches",
        "existing_count",
        "items",
        "first_branches",
        "first_value",
        "last_branches",
        "last_value",
        "length",
    )

    def __init__(self, length:int, items:dict[tuple[int,...],Dt1]) -> None:
        '''
        :length: The total number of branches.
        :items: The dictionary (sorted by branches) of (branches that have this item) to (value at those branches).
        '''
        if len(items) == 0:
            raise Exceptions.DiffExistenceError(self)
        self.items = items
        '''
        The dictionary of (branches that have this item) to (value at those branches).
        '''
        self.branches = {
            branch: branches
            for branches in self.items.keys()
            for branch in branches
        }
        '''
        Mapping of each branch to the tuple of branches that it is in.
        '''
        self.length = length
        '''
        The total number of branches.
        '''
        self.existing_count = len(items)
        '''
        The number of items that exist in this Diff so far.
        '''
        first_item = next(iter(self.items.items()))
        self.first_branches = first_item[0]
        '''
        The tuple of branches that the earliest value is from.
        '''
        self.first_value = first_item[1]
        '''
        The earliest value in this Diff.
        '''
        last_item = next(iter(reversed(self.items.items())))
        self.last_branches = last_item[0]
        '''
        The tuple of branches that the latest value is from.
        '''
        self.last_value = last_item[1]
        '''
        The latest value in this Diff.
        '''

    def iter(self) -> Iterable[tuple[tuple[int,...],Dt1]]:
        return self.items.items()

    def append(self, new_branch:int, new_value:Dt1) -> "Diff[Dt1]":
        '''
        Returns a new Diff with the new value added onto the current items.
        
        :new_branch: The branch that the value is from.
        :new_value: The new value.
        '''
        if new_branch in self.branches:
            raise Exceptions.DiffContinuityError(list(self.branches.keys()), new_branch)
        items_copy = self.items.copy()
        items_copy[(new_branch,)] = new_value
        return Diff(self.length, items_copy)


    def with_last_as(self, new_branch:int, new_value:"Dt1|Diff[Dt1]") -> "Diff[Dt1]":
        '''
        Returns a new Diff with the new value added onto the current items.
        
        If `new_value` is not a Diff, then it modifies the last branches to include `new_branch`.
        
        If `new_value` is a Diff, then it adds a new branches with the `new_value`'s last value.
        
        :new_branch: The branch that the value or the newer part of the value is from.
        :new_value: The new value.
        '''
        if new_branch in self.branches:
            raise Exceptions.DiffContinuityError(list(self.branches.keys()), new_branch)
        if isinstance(new_value, Diff):
            # different item must have a new branches.
            assert new_value.existing_count == 2 # if this is not true then it's being used wrong
            # assert self.last_value == new_value.first_value # This should be True always, but is expensive to check.
            items_copy = self.items.copy()
            items_copy[(new_branch,)] = new_value.last_value
        else:
            # same item can be appended onto the current last branches.
            new_branches = tuple(list(self.last_branches) + [new_branch])
            items_copy:dict[tuple[int,...],Dt1] = self.items.copy()
            del items_copy[self.last_branches]
            items_copy[new_branches] = new_value
        return Diff(self.length, items_copy)

    def extend(self, new_branch:int) -> "Diff[Dt1]":
        '''
        Returns a new Diff with the latest value also in the `new_branch` branch.
        ```python
        diff.with_last_as(new_branch, diff.last_value)
        # is the same as
        diff.extend(new_branch)
        ```
        
        :new_branch: The branch that the latest value is also a part of.
        '''
        if new_branch in self.branches:
            raise Exceptions.DiffContinuityError(list(self.branches.keys()), new_branch)
        new_branches = tuple(list(self.last_branches) + [new_branch])
        items_copy:dict[tuple[int,...],Dt1] = self.items.copy()
        del items_copy[self.last_branches]
        items_copy[new_branches] = self.last_value
        return Diff(self.length, items_copy)

    def __getitem__(self, index:int|tuple[int,...]) -> Dt1:
        if isinstance(index, int):
            branches = self.branches.get(index)
            if branches is None:
                raise Exceptions.DiffKeyError(index, self)
            return self.items[branches]
        else:
            output = self.items.get(index, ...)
            if output is ...:
                raise Exceptions.DiffKeyError(index, self)
            return output

    def __contains__(self, index:int|tuple[int,...]) -> bool:
        if isinstance(index, int):
            return index in self.branches
        else:
            return index in self.items

    def get(self, index:int|tuple[int,...]) -> Dt1|_NoExistType:
        '''
        Returns the same as __getitem__, but returns NoExist instead of raising
        an exception if the item does not exist.
        '''
        if isinstance(index, int):
            branches = self.branches.get(index)
            if branches is None:
                return NoExist
            return self.items[branches]
        else:
            return self.items.get(index, NoExist)

    def get_change_branches(self, include_zero:bool=True) -> list[int]:
        '''
        Returns the branch at the start of each change, including empty areas.
        
        :include_zero: Whether to include zero if it is not NoExist.
        '''
        output:list[int] = []
        last_item:Any = NoExist
        for branch in range(self.length):
            item = self.get(branch)
            if item is not last_item:
                if (include_zero or branch != 0):
                    output.append(branch)
                last_item = item
        return output

    def __repr__(self) -> str:
        return f"<Diff {" → ".join(f"{item} at {index[0] if len(index) == 1 else index}" for index, item in self.items.items())}>"

    def __hash__(self) -> int:
        return hash(tuple(self.items.items()))

    def __len__(self) -> int:
        return len(self.items)

    def __lt__(self, other:Any) -> bool:
        if isinstance(other, Diff):
            return self.last_value < other.last_value
        else:
            return self.last_value < other

    def __gt__(self, other:Any) -> bool:
        if isinstance(other, Diff):
            return self.last_value > other.last_value
        else:
            return self.last_value > other

    def __eq__(self, value: object) -> bool:
        return self.length == value.length and self.items == value.items if isinstance(value, Diff) else False

def iter_diff[a](item:a|Diff[a]) -> Iterable[tuple[tuple[int,...]|None,a]]:
    if isinstance(item, Diff):
        yield from item.iter()
    else:
        yield None, item

def double_iter_diff[a, b](item1:a|Diff[a], item2:b|Diff[b]) -> Iterable[tuple[tuple[int,...]|None,a,b]]:
    match item1, item2:
        case Diff(), Diff():
            item1_diff, item2_diff = cast("Diff[a]", item1), cast("Diff[b]", item2)
            boundaries:list[int] = [branches[-1] for branches in item1_diff.items]
            boundaries.extend(branches[-1] for branches in item2_diff.items)
            boundaries = sorted(set(boundaries))
            current_branches:list[int] = []
            current_boundary_index = 0
            for branch1, branch2 in zip(item1_diff.branches, item2_diff.branches):
                assert branch1 == branch2
                current_branches.append(branch1)
                if branch1 == boundaries[current_boundary_index]:
                    # If this branch is the last one in this bunch.
                    yield tuple(current_branches), item1_diff[branch1], item2_diff[branch1]
                    current_branches = []
                    current_boundary_index += 1 # this will not result in an out-of-bounds error.
        case Diff(), _:
            item1_diff, item2_object = cast("Diff[a]", item1), cast(b, item2)
            for branches, item1_iter in iter_diff(item1):
                yield branches, item1_iter, item2_object
            yield None, item1_diff.last_value, item2_object
        case _, Diff():
            item1_object, item2_diff = cast(a, item1), cast("Diff[b]", item2)
            for branches, item2_iter in iter_diff(item2):
                yield branches, item1_object, item2_iter
            yield None, item1_object, item2_diff.last_value
        case _, _:
            item1_object, item2_object = cast(a, item1), cast(b, item2)
            yield None, item1_object, item2_object

def last_value[a, b](item:a|Diff[b]) -> a|b:
    '''
    Returns the last value if the item is a Diff,
    and just the item otherwise.

    :item: The Diff or non-Diff.
    '''
    if isinstance(item, Diff):
        return item.last_value
    else:
        return item

def last_value_with_branch[a, b](item:a|Diff[b]) -> tuple[a|b,int]:
    '''
    Returns the last value if the item is a Diff, and just the item otherwise.
    Also returns the branch (-1 if not a Diff).
    
    :item: The Diff or non-Diff.
    '''
    if isinstance(item, Diff):
        return item.last_value, item.last_branches[-1]
    else:
        return item, -1
