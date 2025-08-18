import traceback
from enum import Enum
from pathlib import Path
from types import TracebackType
from typing import Callable, Iterator, Literal, Mapping, Self, Sequence


class FocusType(Enum):
    focus = "~"
    highlight = "^"

class Reader():

    __slots__ = (
        "_lines",
        "_newlines",
        "exceptions",
        "file_name",
        "index",
        "path",
        "source",
        "trace",
    )

    def __init__(self, source:str, file_name:str, path:Path) -> None:
        self.source:str = source
        self.file_name = file_name
        self.path = path
        self.index:int = 0
        self._newlines:Mapping[int,tuple[int, int]]|None = None # mapping of index to line number and index within line
        self._lines:Sequence[str]
        self.trace:list[TraceObject] = []
        self.exceptions:list[ReaderTrace] = []

    def read(self, amount:int, back:int=0, /) -> str:
        if self.index >= len(self.source):
            self.index = len(self.source)
            return ""
        elif self.index + amount > len(self.source):
            output = self.source[self.index:]
            self.index = min(len(self.source), self.index + amount - back)
        else:
            output = self.source[self.index:self.index+amount]
            self.index += amount - back
        return output

    def next_is(self, text:str, /, reverse_if_false:bool, reverse_if_true:bool) -> bool:
        """
        Returns True if the next `len(text)` characters are `text`.
        """
        output = self.read(len(text), len(text)) == text
        if not (reverse_if_false and not output or reverse_if_true and output):
            self.move(len(text))
        return output

    def next_in(self, texts:Sequence[str], /, reverse_if_false:bool, reverse_if_true:bool) -> bool:
        """
        Returns True if the next characters are in texts. `texts` must have strings of equal length.
        """
        if len(texts) == 0: return False
        length = len(texts[0])
        output = self.read(length, length) in texts
        if not (reverse_if_false and not output or reverse_if_true and output):
            self.move(length)
        return output

    def set(self, index:int, /) -> None:
        self.index = index

    def move(self, amount:int, /) -> None:
        self.index = min(self.index + amount, len(self.source))

    def at_last(self, amount:int=1, /) -> bool:
        """
        Returns if the Reader is unable to read due to being at the end of its source.

        :param amount: The number of characters the Reader may be able to read.
        """
        return self.index + amount > len(self.source)

    def read_while(self, while_function:Callable[[str],bool]) -> str:
        """
        Returns all characters from the current position while `while_function` returns True
        or the end of the source is reached.

        :param while_function: A function that takes a single character.
        """
        start = self.index
        for index in range(start, len(self.source)):
            if not while_function(self.source[index]):
                self.index = index
                return self.source[start:index]
        self.index = len(self.source)
        return self.source[start:]

    def move_while(self, while_function:Callable[[str],bool]) -> int:
        """
        Moves forward while `while_function` returns True or the end of the source is reached.
        Returns the amount moved.

        :param while_function: A function that takes a single character.
        """
        start = self.index
        for index in range(start, len(self.source)):
            if not while_function(self.source[index]):
                self.index = index
                return self.index - start
        self.index = len(self.source)
        return self.index - start

    def current_scope(self) -> "TraceObject":
        """
        Returns the TraceObject of the current scope.
        Contains information on the stop and start of this object.
        """
        return self.trace[-1]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.index}/{len(self.source)} \"{self.file_name}\">"

    def __enter__(self) -> Self:
        return self

    def focus(self) -> Self:
        """
        If an exception occurs in this `with` block, highlight the contents read during it with "~". Low-priority.
        """
        self.trace.append(HighlightObject(self.index, FocusType.focus))
        return self

    def highlight(self) -> Self:
        """
        If an exception occurs in this `with` block, highlight the contents read during it with "^". High-priority.
        """
        self.trace.append(HighlightObject(self.index, FocusType.highlight))
        return self

    def __exit__(self, exc_type:type[BaseException]|None, exc_value:BaseException|None, traceback:TracebackType) -> Literal[False]:
        this_item = self.trace.pop().set_end_index(self.index)
        if len(self.trace) == 0:
            self.exceptions.extend(this_item.exceptions)
        else:
            self.trace[-1].add_exceptions(this_item.exceptions)
        return False

    @property
    def has_exceptions(self) -> bool:
        return len(self.exceptions) > 0

    @property
    def exception_count(self) -> int:
        return len(self.exceptions)

    def exception(self, exception:Exception) -> Self:
        if len(self.trace) == 0:
            self.exceptions.append(ReaderTrace(exception, ()))
        else:
            self.trace[-1].exceptions.append(ReaderTrace(exception, self.trace.copy()))
        return self

    @property
    def newlines(self) -> Mapping[int,tuple[int,int]]:
        if self._newlines is None:
            newlines:dict[int,tuple[int, int]] = {}
            line_count:int = 1
            line_index:int = 1 # index within line
            for index, char in enumerate(self.source):
                newlines[index] = (line_count, line_index)
                if char == "\n":
                    line_count += 1
                    line_index = 1
                line_index += 1
            # some Fields may consider themselves to end on the EOF.
            newlines[len(newlines)] = newlines[len(newlines) - 1]
            self._newlines = newlines
            self._lines = self.source.splitlines()
        return self._newlines

    @property
    def lines(self) -> Sequence[str]:
        self.newlines
        return self._lines

    def _lines_trim_indentation(self, lines:Sequence[str]) -> tuple[Sequence[str], int]:
        minimum_indentation:int = max(len(line) for line in lines)
        for line in lines:
            trimmed_length = len(line) - len(line.lstrip(" "))
            minimum_indentation = min(minimum_indentation, trimmed_length)
        indentation = " " * minimum_indentation
        return [line.removeprefix(indentation) for line in lines], minimum_indentation

    def stringify_exceptions(self) -> Iterator[str]:
        for reader_trace in self.exceptions:
            output:list[str] = [f"Syntax error ({reader_trace.exception.__class__.__name__}):"]
            if len(reader_trace.trace) == 0:
                output.append(f"  File \"{self.path}\", in {self.file_name}")
            else:
                last_trace_object = reader_trace.trace[-1]
                start_line, start_column = self.newlines[last_trace_object.start_index]
                end_line, end_column = self.newlines[last_trace_object.end_index]
                output.append(f"  File \"{self.path}\", line {start_line}, in {self.file_name}")
                text = self.lines[start_line-1:end_line] # weird offset because lines start counting from 1
                text_lines, indentation_offset = self._lines_trim_indentation(text)
                for index, line in enumerate(text_lines):
                    output.append(f"    {line}")
                    if index == 0 and index == len(text_lines) - 1:
                        output.append(f"{" " * (2 + start_column - indentation_offset)}{"~" * (end_column - start_column)}")
                    elif index == 0:
                        output.append(f"{" " * (2 + start_column - indentation_offset)}{"~" * (len(line) - start_column + indentation_offset)}")
                    elif index == len(text_lines) - 1:
                        output.append(f"    {"~" * (end_column - indentation_offset)}")
                    else: # full line
                        output.append(f"    {"~" * (len(line) - indentation_offset)}")
            output.append("".join(traceback.format_exception(reader_trace.exception)).rstrip())
            yield "\n".join(output)

class TraceObject():

    __slots__ = (
        "end_index",
        "exceptions",
        "start_index",
    )

    def __init__(self, start_index:int) -> None:
        self.start_index = start_index
        self.exceptions:list[ReaderTrace] = []

    def add_exceptions(self, exceptions:Sequence["ReaderTrace"], /) -> None:
        self.exceptions.extend(exceptions)

    def set_end_index(self, end_index:int) -> Self:
        self.end_index = end_index
        return self

class HighlightObject(TraceObject):

    __slots__ = (
        "focus_type",
    )

    def __init__(self, start_index: int, focus_type: FocusType) -> None:
        super().__init__(start_index)
        self.focus_type = focus_type

class ReaderTrace():

    __slots__ = (
        "exception",
        "trace",
    )

    def __init__(self, exception:Exception, trace:Sequence[TraceObject]) -> None:
        self.exception = exception
        self.trace = trace
