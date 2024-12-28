import traceback
from typing import Any, Hashable, Self

import Utilities.Exceptions as Exceptions


class ErrorTrace():

    __slots__ = (
        "already_added_names",
        "data",
        "exception",
        "is_final",
        "trace",
    )

    def __init__(self, exception:Exception, current_pos_name:str|None, current_pos_key:Hashable|None, data:Any|None) -> None:
        '''
        :exception: The Exception that this ErrorTrace envelops.
        :current_pos_name: The name of the current Structure.
        :current_pos_key: Where in the current Structure the error occurs.
        :data: The data at the current position in the Structure.
        '''
        self.exception = exception
        self.is_final = False
        self.trace:list[_TraceItem] = []
        self.data = data
        self.already_added_names:set[str] = set()
        if current_pos_name is not None:
            self.add(current_pos_name, current_pos_key)

    def add(self, current_pos_name:str, current_pos_key:Hashable|None, force:bool=False) -> Self:
        '''
        Adds a Structure to the list of Structures. Returns itself.
        :current_pos_name: The name of the current Structure.
        :current_pos_key: Where in the current Structure the error occurs.
        :force: If True, adds it even if current_pos_name is duplicate.
        '''
        if self.is_final:
            raise Exceptions.TraceError(self, self.add, self.is_final)
        if force or current_pos_name not in self.already_added_names:
            self.trace.append(_TraceItem(current_pos_name, current_pos_key))
            self.already_added_names.add(current_pos_name)
        return self

    def copy(self) -> Self:
        '''
        Copies this ErrorTrace.
        '''
        output = type(self)(self.exception, None, None, self.data)
        output.is_final = self.is_final
        output.trace = self.trace.copy()
        output.already_added_names = self.already_added_names
        return output

    def finalize(self) -> Self:
        """
        Prevents any more Structures from being added to this ErrorTrace.
        Returns itself.
        """
        if self.is_final:
            raise Exceptions.TraceError(self, self.finalize, self.is_final)
        self.is_final = True
        self.trace.reverse()
        return self

    def stringify(self) -> str:
        "Returns a string representing the ErrorTrace. Can only be called after `finalize`."
        if not self.is_final:
            raise Exceptions.TraceError(self, self.stringify, self.is_final)
        trace_string = "→".join(str(trace_item) for trace_item in self.trace)
        exception_lines = traceback.format_exception(self.exception)
        if self.data is None:
            return f"Exception at {trace_string}:\n{"".join(exception_lines)}"
        else:
            data_string = str(self.data)
            return f"Exception at {trace_string} from data {data_string}:\n{"".join(exception_lines)}"

    def __repr__(self) -> str:
        finalized_str = "finalized" if self.is_final else "unfinalized"
        return f"<ErrorTrace {finalized_str} len {len(self.trace)}>"

class _TraceItem():
    "A piece of an ErrorTrace containing the name of a Structure and the position inside it."

    def __init__(self, name:str, key:Hashable|None) -> None:
        '''
        :name: The name of the current Structure.
        :key: The position in the current Structure.
        '''
        self.name = name
        self.key = key

    def __str__(self) -> str:
        if self.key is None:
            return self.name
        else:
            return f"{self.name}[{self.key}]"

    def __repr__(self) -> str:
        if self.key is None:
            return f"<{self.__class__.__name__} {self.name}>"
        else:
            return f"<{self.__class__.__name__} {self.name}[{self.key}]>"
