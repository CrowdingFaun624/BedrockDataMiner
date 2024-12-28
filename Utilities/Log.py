import enum
import json
from pathlib import Path
from typing import Any, TypeGuard, cast

import Utilities.Exceptions as Exceptions


class LogType(enum.Enum):
    lines = "lines"
    json_lines = "json_lines"

ALLOWED_TYPES:dict[LogType, tuple[type,...]] = {
    LogType.lines: (str,),
    LogType.json_lines: (dict, list, str, int, float, bool, type(None))
}

class Log[T]():

    def __init__(self, name:str, file:Path, log_type:LogType, reset_on_reload:bool) -> None:
        self.name:str = name
        self.file:Path = file
        self.log_type = log_type
        self.reset_on_reload:bool = reset_on_reload
        self.file.touch()
        if reset_on_reload:
            self.file.write_text("")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name} {self.log_type.value}>"

    def supports_type[A](self, log:"Log[Any]", _type:type[A]) -> TypeGuard["Log[A]"]:
        return any(issubclass(_type, allowed_type) for allowed_type in ALLOWED_TYPES[self.log_type])

    def write(self, data:T) -> T:
        if not isinstance(data, (allowed_types := ALLOWED_TYPES.get(self.log_type, (object,)))):
            raise Exceptions.LogWriteTypeError(self, type(data), allowed_types)
        with open(self.file, "at", encoding="UTF8") as f:
            match self.log_type:
                case LogType.lines:
                    data_string = cast(str, data)
                    if not data_string.endswith("\n"):
                        data_string += "\n"
                    f.write(data_string)
                case LogType.json_lines:
                    f.write(json.dumps(data) + "\n")
        return data
