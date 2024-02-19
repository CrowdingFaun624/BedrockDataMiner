import enum
from typing import Any, Generic, TypeVar

class NoExist(): # class that is different from None

    def __hash__(self) -> int:
        return hash(None)

    def __str__(self) -> str:
        raise NotImplementedError("Attempted to stringify NoExist object!")

class ChangeType(enum.Enum):
    removal = "removal"
    change = "change"
    addition = "addition"

class DiffType(enum.Enum):
    new = "new"
    old = "old"
    not_diff = "not_diff"

exist_change_type = {
    (False, True): ChangeType.addition,
    (True, False): ChangeType.removal,
    (True, True): ChangeType.change,
}

Dt1 = TypeVar("Dt1")
Dt2 = TypeVar("Dt2")
Dt3 = TypeVar("Dt3")
Dt4 = TypeVar("Dt4")

class Diff(Generic[Dt1,Dt2]):

    def __init__(self, old:Dt1=NoExist(), new:Dt2=NoExist()) -> None:
        if old == new:
            raise ValueError("`old` is equal to `new`!")
        if isinstance(old, Diff):
            raise TypeError("`old` is a Diff!")
        if isinstance(new, Diff):
            raise TypeError("`new` is a Diff!")
        if isinstance(old, NoExist) and isinstance(new, NoExist):
            raise ValueError("Neither `old` nor `new` exist!")

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
        if self.is_addition: return [(self.new, DiffType.new)]
        elif self.is_change: return [(self.old, DiffType.old), (self.new, DiffType.new)]
        elif self.is_removal: return [(self.old, DiffType.old)]

    def __getitem__(self, index:ChangeType) -> Dt1|Dt2:
        if index is DiffType.new:
            if isinstance(self.new, NoExist):
                raise KeyError("%s does not have a new object!" % repr(self))
            else: return self.new
        elif index is DiffType.old:
            if isinstance(self.old, NoExist):
                raise KeyError("%s does not have an old object!" % repr(self))
            else: return self.old
        elif index is DiffType.not_diff:
            raise KeyError("Attempted to get an item of %s using a `DiffType.not_diff` key!" % repr(self))
        else:
            raise KeyError("Attempted to get an item of %s using a non-DiffType key!" % repr(self))

    def __repr__(self) -> str:
        if self.is_addition:
            return "<Diff add %s>" % (self.new)
        elif self.is_change:
            return "<Diff change %s -> %s>" % (self.old, self.new)
        elif self.is_removal:
            return "<Diff remove %s>" % (self.old)

    def __str__(self) -> str:
        if self.is_addition:
            return "Addition of %s" % (self.new)
        elif self.is_change:
            return "%s -> %s" % (self.old, self.new)
        elif self.is_removal:
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

def iter_diff(thing:a|Diff[Dt1,Dt2]) -> list[tuple[a|Dt1|Dt2,DiffType]]:
    if isinstance(thing, Diff):
        return thing.iter()
    else:
        return [(thing, DiffType.not_diff)]

def double_iter_diff(thing1:a|Diff[Dt1,Dt2], thing2:b|Diff[Dt3,Dt4]) -> list[tuple[a|Dt1|Dt2,b|Dt3|Dt4,DiffType,DiffType]]:
    thing1_iter = iter_diff(thing1)
    thing2_iter = iter_diff(thing2)
    if len(thing1_iter) == 2 or len(thing2_iter) == 2:
        if len(thing1_iter) == 1: thing1_iter = (thing1_iter[0], thing1_iter[0])
        if len(thing2_iter) == 1: thing2_iter = (thing2_iter[0], thing2_iter[0])
    return [(iter1[0], iter2[0], iter1[1], iter2[1]) for iter1, iter2 in zip(thing1_iter, thing2_iter)]

def get_diff_types(thing:object|Diff) -> tuple[DiffType,...]:
    if isinstance(thing, Diff):
        if thing.is_addition: return (DiffType.new,)
        elif thing.is_change: return (DiffType.old, DiffType.new)
        elif thing.is_removal: return (DiffType.old,)
    else:
        return (DiffType.not_diff,)
