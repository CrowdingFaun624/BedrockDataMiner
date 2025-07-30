import enum
import traceback
from types import EllipsisType, NoneType, TracebackType
from typing import Any, Callable, Iterable, Iterator, Self

from Utilities.Exceptions import TypeVerificationFailedError, TypeVerifierException


class TraceType(enum.Enum):
    object = 0
    key = 1
    key_group = 2

def simplify_trace(trace:list[tuple[object, Callable[[],str], Any|EllipsisType, TraceType]]) -> list[tuple[object, Callable[[],str], Any, TraceType]]:
    last_id:int|None = None
    last_trace_type:TraceType|None = None
    output:list[tuple[object, Callable[[],str], Any, TraceType]] = []
    for thing, name, value, trace_type in trace:
        object_id = id(thing)
        if object_id != last_id or trace_type != last_trace_type:
            last_id = object_id
            last_trace_type = trace_type
            output.append((thing, name, value, trace_type))
        else:
            output[-1] = (thing, name, value, trace_type)
    return output

def stringify_trace(trace:list[tuple[object, Callable[[],str], Any|EllipsisType, TraceType]]) -> str:
    if len(trace) == 0:
        return "empty"
    else:
        trace_string:list[str] = []
        for index, (thing, position_name_function, position_data, trace_type) in enumerate(simplify_trace(trace)):
            position_name = position_name_function()
            match trace_type:
                case TraceType.object:
                    if index == 0:
                        trace_string.append(position_name)
                    else:
                        trace_string.append(f" → {position_name}")
                case TraceType.key:
                    trace_string.append(f"[{position_name}]")
                case TraceType.key_group:
                    assert isinstance(thing, tuple)
                    trace_string.append("".join(f"[{str(key)}]" for key in thing))
        return "".join(trace_string)

class Trace():

    __slots__ = (
        "_exceptions",
        "trace",
    )

    def __init__(self) -> None:
        self._exceptions:list[ErrorTrace] = []
        self.trace:list[tuple[object, Callable[[],str], Any|EllipsisType, TraceType]] = []

    def breakpoint(self, items:list[str]) -> bool:
        return items == [item[1]() for item in self.trace]

    def get_breakpoint_data(self) -> list[str]:
        return [item[1]() for item in self.trace]

    def enter(self, object:object, position_name:str, position_data:Any|EllipsisType) -> Self:
        '''
        This method must be used at a `with` statement.
        :object: The current Structure or StructureBase.
        :position_name: The name of the current Structure or StructureBase.
        :position_data: The value that the context is now looking at.
        '''
        self.trace.append((object, lambda: position_name, position_data, TraceType.object))
        return self

    def enter_key(self, key:object, position_data:Any|EllipsisType) -> Self:
        '''
        This method must be used at a `with` statement.
        :key: The current key of the context.
        :position_data: The value that the context is now looking at.
        '''
        self.trace.append((key, lambda: str(key), position_data, TraceType.key))
        return self

    def enter_keys(self, keys:tuple[object,...], position_data:Any|EllipsisType) -> Self:
        '''
        This method must be used at a `with` statement.
        :keys: The current key group of the context.
        :position_data: The value that the context is now looking at.
        '''
        # trace[1] is empty string because it isn't used.
        self.trace.append((keys, lambda: "", position_data, TraceType.key_group))
        return self

    def include(self, trace:"Trace") -> None:
        '''
        Combines this Trace with another Trace.
        '''
        self._exceptions.extend(ErrorTrace(self.trace + exception.trace, exception.exception) for exception in trace._exceptions)

    @property
    def objects(self) -> Iterable[tuple[object, Callable[[],str], Any, TraceType]]:
        '''
        Generator of all objects that created an Exception.
        '''
        yield from (trace_item for error_trace in self._exceptions for trace_item in error_trace.trace)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type:type[BaseException]|None, exc_value:BaseException, traceback:TracebackType) -> bool:
        match exc_value:
            case NoneType():
                output = False
            case Exception() | ExceptionGroup():
                self.exception(exc_value)
                output = True # suppress further raising
            case BaseException():
                output = False # do not suppress BaseException, like ctrl+C.
        self.trace.pop()
        return output

    def exception(self, exception:Exception) -> None:
        '''
        :exception: The Exception to store in this Trace.
        '''
        self._exceptions.append(ErrorTrace(self.trace.copy(), exception))

    def exceptions(self, exceptions:Iterable[Exception]) -> None:
        for exception in exceptions:
            self.exception(exception)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {stringify_trace(self.trace)}>"

    def __len__(self) -> int:
        return len(self._exceptions)

    @property
    def has_exceptions(self) -> bool:
        return any(not isinstance(error_trace.exception, (TypeVerificationFailedError, TypeVerifierException)) for error_trace in self._exceptions)

    @property
    def exception_count(self) -> int:
        return sum(not isinstance(error_trace.exception, (TypeVerificationFailedError, TypeVerifierException)) for error_trace in self._exceptions)

    def show_data(self, error_trace:"ErrorTrace") -> str:
        output = repr(error_trace.trace[-1][2])
        if len(output) > 1000:
            output = output[:500] + " ... " + output[-500:]
        return output

    def stringify(self) -> Iterator[str]:
        '''
        Turns each stored Exception into a fancy, formatted string.
        '''
        for error_trace in self._exceptions:
            exception = error_trace.exception
            match exception:
                case TypeVerificationFailedError(): # completely useless.
                    continue
                case TypeVerifierException(): # Trace of TypeVerificationExceptions are useless and space-hungry.
                    exception_string = str(exception)
                case _:
                    exception_string = "".join(traceback.format_exception(error_trace.exception)).rstrip()
            yield f"{error_trace.exception.__class__.__name__} at {stringify_trace(error_trace.trace)}{f" from data {self.show_data(error_trace)}" if len(error_trace.trace) > 0 and error_trace.trace[-1][2] is not ... else ""}:{"\n" if exception_string.count("\n") > 0 else " "}{exception_string}"

class ErrorTrace():

    __slots__ = (
        "exception",
        "trace",
    )

    def __init__(self, trace:list[tuple[object, Callable[[],str], Any, TraceType]], exception:Exception) -> None:
        '''
        An ErrorTrace should not be created by this method; instead, use `Trace.exception`.
        :trace: A copy of the Trace object's `trace` list attribute.
        :exception: The Exception that occurred.
        '''
        self.trace = trace
        self.exception = exception

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.exception.__class__.__name__} {stringify_trace(self.trace)}>"
