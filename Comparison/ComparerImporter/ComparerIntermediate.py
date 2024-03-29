from typing import TypeVar

import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerSection as ComparerSection

ComparerGeneric = TypeVar("ComparerGeneric", ComparerTyping.DictComparerTypedDict, ComparerTyping.ListComparerTypedDict, ComparerTyping.TypedDictComparerTypedDict)

class ComparerIntermediate(Intermediate.Intermediate[ComparerGeneric]): # just for type hints lol

    my_type:list[type]

    def __init__(self, data: ComparerGeneric, name: str, index: int) -> None:
        self.name = name
        self.final:ComparerSection.ComparerSection|None = None