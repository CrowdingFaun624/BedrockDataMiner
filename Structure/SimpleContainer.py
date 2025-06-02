from typing import Mapping, cast

import Domain.Domain as Domain
import Structure.Container as Con


def sdon_from_bundles[A](bundles:Mapping[tuple[int,...],A], domain:"Domain.Domain") -> "SDon[A]":
    containers:Mapping[int, SCon[A]] = {}
    for bundle, item in bundles.items():
        container = SCon(item, domain)
        containers.update((branch, container) for branch in bundle)
    return SDon(containers)

class SCon[A](Con.Con[A]):

    __slots__ = (
        "data",
        "hash",
    )

    def __init__(self, data:A, domain:"Domain.Domain") -> None:
        self.data = data
        self.hash = domain.type_stuff.hash_data(data)

    def as_don(self, bundle:tuple[int,...]) -> "SDon[A]":
        return SDon({branch: self for branch in bundle})

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {repr(self.data)}>"

class SDon[A](Con.Don[A]):

    __slots__ = (
        "_containers",
        "hash",
    )

    def __init__(self, containers:Mapping[int,SCon[A]]) -> None:
        self._containers:Mapping[int,SCon[A]] = containers
        self.hash = hash(tuple((hash(key), hash(value)) for key, value in containers.items()))

    def get_con(self, branch:int) -> "SCon[A]":
        return self._containers[branch]

    @property
    def last_container(self) -> SCon[A]:
        return self._containers[cast(int, next(iter(reversed(self._containers))))]

    def __repr__(self) -> str:
        combined_data:list[tuple[tuple[int,...], SCon[A]]] = []
        current_bundle:list[int] = []
        last_item:SCon[A]|None = None
        for branch, item in self._containers.items():
            if last_item is None or item is last_item:
                if last_item is None:
                    last_item = item
                current_bundle.append(branch)
            else:
                combined_data.append((tuple(current_bundle), last_item))
                last_item = item
                current_bundle = []
        assert last_item is not None
        combined_data.append((tuple(current_bundle), last_item))
        if len(combined_data) == 1:
            # Since these usually appear in Diffs, branch information is unnecessary when it's all one bundle.
            return f"<{self.__class__.__name__} {repr(last_item.data)}>"
        else:
            return f"<{self.__class__.__name__} {" → ".join(f"{repr(item)} at {index[0] if len(index) == 1 else index}" for index, item in combined_data)}>"
