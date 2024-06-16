import enum
from typing import Any, Generic, NoReturn, Sequence, TypeVar

import Utilities.Exceptions as Exceptions


class NoExist():
    "Class that is different from None."

    def __hash__(self) -> int:
        return hash(None)

    def __str__(self) -> NoReturn:
        raise Exceptions.CannotStringifyError(NoExist)

class ChangeType(enum.Enum):
    removal = "removal"
    change = "change"
    addition = "addition"

class DiffType(enum.Enum):
    new = "new"
    old = "old"
    not_diff = "not_diff"

exist_change_type:dict[tuple[bool,bool],ChangeType] = {
    (False, True): ChangeType.addition,
    (True, False): ChangeType.removal,
    (True, True): ChangeType.change,
}

Dt1 = TypeVar("Dt1")
Dt2 = TypeVar("Dt2")
Dt3 = TypeVar("Dt3")
Dt4 = TypeVar("Dt4")

class Diff(Generic[Dt1,Dt2]):
    "A difference in data from an old version to a new version."

    def __init__(self, old:Dt1=NoExist(), new:Dt2=NoExist()) -> None:
        '''
        :old: The older version of data.
        :new: The newer version of data.
        '''
        self.old:Dt1 = old
        self.new:Dt2 = new
        self.change_type = exist_change_type[not isinstance(old, NoExist), not isinstance(new, NoExist)]
        self.is_addition = self.change_type == ChangeType.addition
        self.is_change = self.change_type == ChangeType.change
        self.is_removal = self.change_type == ChangeType.removal

    def first_existing_property(self) -> Dt1|Dt2:
        '''Returns `self.new` if `self.new` is not NoExist, otherwise `self.old`.'''
        if self.is_removal:
            return self.old
        else:
            return self.new

    def iter(self) -> list[tuple[Dt1|Dt2,DiffType]]:
        "Returns each existing member of this Diff from oldest to newest."
        match self.change_type:
            case ChangeType.addition:
                return [(self.new, DiffType.new)]
            case ChangeType.change:
                return [(self.old, DiffType.old), (self.new, DiffType.new)]
            case ChangeType.removal:
                return [(self.old, DiffType.old)]

    def __getitem__(self, index:DiffType) -> Dt1|Dt2:
        match index:
            case DiffType.new:
                if isinstance(self.new, NoExist):
                    raise Exceptions.DiffKeyError(index, self)
                else: return self.new
            case DiffType.old:
                if isinstance(self.old, NoExist):
                    raise Exceptions.DiffKeyError(index, self)
                else: return self.old
            case DiffType.not_diff:
                raise Exceptions.DiffKeyError(index, self)

    def __repr__(self) -> str:
        match self.change_type:
            case ChangeType.addition:
                return "<Diff add %s>" % (self.new)
            case ChangeType.change:
                return "<Diff change %s -> %s>" % (self.old, self.new)
            case ChangeType.removal:
                return "<Diff remove %s>" % (self.old)

    def __str__(self) -> str:
        match self.change_type:
            case ChangeType.addition:
                return "Addition of %s" % (self.new)
            case ChangeType.change:
                return "%s -> %s" % (self.old, self.new)
            case ChangeType.removal:
                return "Removal of %s" % (self.old)

    def __hash__(self) -> int:
        return hash((self.old, self.new))

    def __lt__(self, other:Any) -> bool:
        if self.is_removal:
            return self.old < other
        else:
            return self.new < other
    def __gt__(self, other:Any) -> bool:
        if self.is_removal:
            return self.old > other
        else:
            return self.new > other

a = TypeVar("a")
b = TypeVar("b")
c = TypeVar("c")

def first_existing_property(item:a|Diff[b,c]) -> a|b|c:
    '''
    Returns the first existing property if the item is a diff,
    and just the item otherwise.
    :item: The Diff or non-Diff.
    '''
    if isinstance(item, Diff):
        return item.first_existing_property()
    else:
        return item

def iter_diff(thing:a|Diff[Dt1,Dt2]) -> Sequence[tuple[a|Dt1|Dt2,DiffType]]:
    '''
    Returns each existing member of this Diff from oldest to newest if it's a Diff,
    otherwise return the item with the `not_diff` DiffType.
    :thing: The data to iterate over.
    '''
    if isinstance(thing, Diff):
        return thing.iter()
    else:
        return [(thing, DiffType.not_diff)]

def double_iter_diff(thing1:a|Diff[Dt1,Dt2], thing2:b|Diff[Dt3,Dt4]) -> list[tuple[a|Dt1|Dt2,b|Dt3|Dt4,DiffType,DiffType]]:
    '''
    Zips the existing members of `thing1` and `thing2`.
    :thing1: The first Diff or non-Diff to iterate over.
    :thing2: The second Diff or non-Diff to iterate over.
    '''
    thing1_iter = iter_diff(thing1)
    thing2_iter = iter_diff(thing2)
    if len(thing1_iter) == 2 or len(thing2_iter) == 2:
        if len(thing1_iter) == 1: thing1_iter = (thing1_iter[0], thing1_iter[0])
        if len(thing2_iter) == 1: thing2_iter = (thing2_iter[0], thing2_iter[0])
    return [(iter1[0], iter2[0], iter1[1], iter2[1]) for iter1, iter2 in zip(thing1_iter, thing2_iter)]

def get_diff_types(thing:object|Diff) -> tuple[DiffType,...]:
    '''
    Returns the DiffTypes of `thing`.
    If `thing` is a Diff, returns DiffTypes based off of the existing members.
    Otherwise, returns (DiffType.not_diff,).
    '''
    if isinstance(thing, Diff):
        match thing.change_type:
            case ChangeType.addition:
                return (DiffType.new,)
            case ChangeType.change:
                return (DiffType.old, DiffType.new)
            case ChangeType.removal:
                return (DiffType.old,)
    else:
        return (DiffType.not_diff,)
