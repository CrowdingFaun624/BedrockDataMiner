from typing import Any

import traceback

class ErrorTrace():

    def __init__(self, exception:Exception, current_pos_name:str|None, current_pos_key:str|int|None, data:Any|None) -> None:
        self.exception = exception
        self.is_final = False
        self.trace:list[_TraceItem] = []
        self.data = data
        self.already_added_names:set[str] = set()
        if current_pos_name is not None:
            self.add(current_pos_name, current_pos_key)

    def add(self, current_pos_name:str, current_pos_key:str|int|None, force:bool=False) -> None:
        if self.is_final:
            raise RuntimeError("Attempted to add to a finalized Trace!")
        if force or current_pos_name not in self.already_added_names:
            self.trace.append(_TraceItem(current_pos_name, current_pos_key))
            self.already_added_names.add(current_pos_name)

    def finalize(self) -> None:
        if self.is_final:
            raise RuntimeError("This Trace is already finalized!")
        self.is_final = True
        self.trace.reverse()

    def stringify(self) -> str:
        if not self.is_final:
            raise RuntimeError("Attempted to stringify a non-finalized Trace!")
        trace_string = ".".join(str(trace_item) for trace_item in self.trace)
        exception_lines = traceback.format_exception(self.exception)
        if self.data is None:
            return "Exception at %s:\n%s" % (trace_string, "\n".join(exception_lines))
        else:
            data_string = str(self.data)
            return "Exception at %s from data %s:\n%s" % (trace_string, data_string, "\n".join(exception_lines))

    def __repr__(self) -> str:
        finalized_str = "finalized" if self.is_final else "unfinalized"
        return "<ErrorTrace %s len %i>" % (finalized_str, len(self.trace))

class _TraceItem():

    def __init__(self, name:str, key:str|int|None) -> None:
        self.name = name
        self.key = key

    def __str__(self) -> str:
        if self.key is None:
            return self.name
        else:
            return "%s[%s]" % (self.name, self.key)

    def __repr__(self) -> str:
        if self.key is None:
            return "<TraceItem %s>" % self.name
        else:
            return "<TraceItem %s[%s]>" % (self.name, self.key)
