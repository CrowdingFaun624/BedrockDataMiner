from typing import AbstractSet, Mapping


class PropagatingVariables():
    """
    Manages propagating booleans and sets.

    :param booleans: A map of boolean propagating variables.
    :param sets: A map of set propagating variables.
    :param subs: Other linked PropagatingVariables.
    :param suggestible: If False, only keys already present will be added from subs.
    """

    __slots__ = (
        "booleans",
        "cached_output",
        "destroyed",
        "sets",
        "subs",
        "suggestible",
    )

    def __init__(self, booleans:Mapping[str, bool], sets:Mapping[str, AbstractSet[object]], subs:list["PropagatingVariables"], suggestible:bool) -> None:
        self.booleans = booleans
        self.sets = sets
        self.subs = subs
        self.suggestible = suggestible
        self.cached_output:tuple[Mapping[str,bool], Mapping[str,AbstractSet[object]]]|None = None
        self.destroyed:bool = False

    @classmethod
    def new_empty(cls, suggestible:bool) -> "PropagatingVariables":
        """
        Creates a new PropagatingVariables with no keys or subs.

        :param suggestible: If False, only keys already present will be added from subs.
        """
        return PropagatingVariables({}, {}, [], suggestible)

    def __hash__(self) -> int:
        return id(self)

    def merge(self, memo:set["PropagatingVariables"]) -> tuple[Mapping[str, bool], Mapping[str,AbstractSet[object]]]:
        """
        :returns: The full booleans and sets from this PropagationVariables and all of its children.
        Will not add new keys that are not already present.
        """
        if self in memo:
            assert self.cached_output is not None # can't be None if it's already been set!
            return self.cached_output
        memo.add(self)
        if self.cached_output is None:
            booleans = dict(self.booleans)
            sets = {key: set(value) for key, value in self.sets.items()}
            self.cached_output = booleans, sets # set early because for caching
            for sub in self.subs:
                new_booleans, new_sets = sub.merge(memo)
                for key, new_boolean in new_booleans.items():
                    if (old_boolean := booleans.get(key)) is not None:
                        booleans[key] = new_boolean or old_boolean
                for key, new_set in new_sets.items():
                    if (old_set := sets.get(key)) is not None:
                        old_set.update(new_set)
        return self.cached_output

    def add(self, *children:"PropagatingVariables|None") -> None:
        """
        When `merge` is called, the outputs from `children` will be added to its output.

        :param children: The PropagatingVariables to add to this one's output. If None, does nothing
        """
        for child in children:
            if child is not None:
                self.cached_output = None # adding a child invalidates the cache.
                self.subs.append(child)

    def destroy(self) -> None:
        """
        Removes attributes of this PropagatingVariables.
        """
        if self.destroyed: return
        self.destroyed = True
        del self.booleans
        del self.sets
        for sub in self.subs:
            sub.destroy()
        del self.subs
        del self.cached_output
