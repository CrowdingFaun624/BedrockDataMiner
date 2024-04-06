'''Modifiers are like Normalizers, but they are applied to a specific class.'''

from typing import Any, TYPE_CHECKING

import Comparison.Trace as Trace

if TYPE_CHECKING:
    import Comparison.ComparerSection as ComparerSection

class Modifier(): # Abstract class

    def __init__(self) -> None:
        self.comparer_section:ComparerSection.ComparerSection|None = None

    def give_comparer_section(self, comparer_section:"ComparerSection.ComparerSection") -> None:
        self.comparer_section = comparer_section

    def modify(self, data:Any, trace:Trace.Trace) -> Any: ...

    def base_modify(self, data:Any, trace:Trace.Trace) -> Any:
        '''Used to transform data before sending it to the regular modify function. Should be the only publically-called function.
        By default, calls the modify function with the same data.'''
        return self.modify(data, trace)
