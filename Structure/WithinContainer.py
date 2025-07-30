from typing import Mapping, cast

from Structure.Container import Con, Don
from Structure.Difference import Diff


def wdon_from_container[A, B:Don, C:Con](containers:Mapping[int,"WCon[A, C]"], insides:B) -> "WDon[A, B, C]":
    return WDon(containers, insides, hash((WDon, insides)))

def wdon_wrap[A, B](comparison:Don[B] | Diff[Don[B]], datas:Mapping[int, "WCon[A, Con[B]]"]) -> "WDon[A, Don[B], Con[B]]|Diff[WDon[A, Don[B], Con[B]]]":
    if isinstance(comparison, Diff):
        new_diff_items:dict[tuple[int,...],WDon[A, Don[B], Con[B]]] = {}
        for bundle, inner_comparison in comparison.items.items():
            new_diff_items[bundle] = wdon_from_container({branch: datas[branch] for branch in bundle}, inner_comparison)
        return Diff(new_diff_items, comparison.contains_diffs)
    else:
        return wdon_from_container(datas, comparison)

class WCon[A, B:Con](Con[A]):

    __slots__ = (
        "data",
        "hash",
        "insides",
    )

    def __init__(self, data:A, insides:B) -> None:
        self.data = data
        self.insides = insides
        self.hash = hash((WCon, insides))

    def as_don(self, bundle:tuple[int,...]) -> "WDon[A, Don, B]":
        return WDon({branch: self for branch in bundle}, self.insides.as_don(bundle), hash((WDon, self.insides)))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.insides}>"

class WDon[A, B:Don, C:Con](Don[A]):

    __slots__ = (
        "_containers",
        "hash",
        "insides",
    )

    def __init__(self, containers:Mapping[int,WCon[A, C]], insides:B, hash:int) -> None:
        self._containers:Mapping[int,WCon[A, C]] = containers
        self.insides = insides
        self.hash = hash

    def get_con(self, branch:int) -> "WCon[A, C]":
        return self._containers[branch]

    @property
    def last_container(self) -> WCon[A, C]:
        return self._containers[cast(int, next(iter(reversed(self._containers))))]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.insides}>"
