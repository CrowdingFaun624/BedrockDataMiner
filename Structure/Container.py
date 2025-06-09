from typing import Iterable, Mapping, cast


class ACon[A]():
    '''
    AbstractContainer, parent of both Con (Container) and Don (DiffContainer).
    For situations where only Containers can be present, use Con.
    '''

    __slots__ = ()
    hash:int

    def __hash__(self) -> int:
        return self.hash

    def __getitem__(self, branch:int) -> A:
        # this method exists so that `Con` can be accessed using __getitem__
        # as well.
        ...

    def get_con(self, branch:int) -> "Con[A]":
        '''
        If self is a Con, returns itself. If self is a Don, returns the Container at `branch`.
        Must not contain Dons or Diffs.
        '''
        ...

    def __eq__(self, value: object) -> bool:
        if isinstance(value, ACon):
            return hash(self) == hash(value)
        else:
            return False

class Con[A](ACon[A]):

    data: A

    __slots__ = (
        "__weakref__",
    )

    def __hash__(self) -> int: # stupid type system forces me to duplicate method.
        return self.hash

    def __getitem__(self, branch:int) -> A:
        return self.data

    def get_con(self, branch: int) -> "Con[A]":
        return self

    def __eq__(self, value: object) -> bool:
        return self.hash == value.hash if isinstance(value, Con) else False

    def as_don(self, bundle:tuple[int,...]) -> "Don[A]":
        '''
        Shallowly transforms self into a Don.
        '''
        ...

class Don[A](ACon[A]):
    '''
    Short for "DiffContainer". Same as a Con but instead of a `data` attribute,
    index this Don using a branch.
    '''

    _containers: Mapping[int,Con[A]]

    __slots__ = ()

    def __hash__(self) -> int: # stupid type system forces me to duplicate method.
        return self.hash

    @property
    def last_value(self) -> A:
        # Fun Fact: reversed(Mapping) returns an iterator of values, but reversed(dict) returns an iterator of keys!
        return self._containers[cast(int, next(iter(reversed(self._containers))))].data

    @property
    def last_container(self) -> Con[A]:
        return self._containers[cast(int, next(iter(reversed(self._containers))))]

    def __getitem__(self, branch: int) -> A:
        return self._containers[branch].data

    def iter_branches(self) -> Iterable[int]:
        return self._containers.keys()

    def get_con(self, branch:int) -> "Con[A]":
        # note: this is duplicated in subclasses for better typing.
        return self._containers[branch]

    def __eq__(self, value: object) -> bool:
        return self is value or (self.hash == value.hash if isinstance(value, Don) else False)
