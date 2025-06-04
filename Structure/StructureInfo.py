from typing import TYPE_CHECKING, Any, Sequence

import Domain.Domain as Domain

if TYPE_CHECKING:
    from Structure.Filter import Filter
    from Structure.Structure import Structure


class StructureInfo():
    '''
    Class defined in each DataminerSettings that is passed to determine behavior.
    '''

    __slots__ = (
        "data",
        "domain",
        "evaluations",
        "hash",
        "parent_name",
    )

    def __init__(self, data:dict[str,Any], domain:"Domain.Domain", parent_name:str) -> None:
        self.data = data
        self.domain = domain
        self.parent_name = parent_name
        self.hash = domain.type_stuff.hash_data(data)
        self.evaluations:dict["Structure",int|None] = {}

    def evaluate(self, structure:"Structure", filters:Sequence["Filter|None"]) -> int|None:
        if (cached_output := self.evaluations.get(structure)) is not None:
            return cached_output
        for index, filter in enumerate(filters):
            if filter is None or filter.filter(self):
                output = index
                break
        else:
            output = None
        self.evaluations[structure] = output
        return output

    def __hash__(self) -> int:
        return self.hash

    def __getitem__(self, key:str) -> Any:
        return self.data[key]

    def __contains__(self, key:str) -> bool:
        return key in self.data

    def get[D](self, key:str, default:D=None) -> Any|D:
        return self.data.get(key, default)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.data}>"
