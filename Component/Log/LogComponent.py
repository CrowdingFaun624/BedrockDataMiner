from typing import Literal, Required, TypedDict

from Component.Component import Component
from Utilities.Exceptions import LogInvalidFileError
from Utilities.Log import Log, LogType
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    EnumTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class LogTypedDict(TypedDict):
    file_name: Required[str]
    log_type: Required[Literal["lines", "json_lines"]]
    reset_on_reload: Required[bool]

class LogComponent(Component[Log, LogTypedDict]):

    type_name = "Log"
    object_type = Log
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("file_name", True, str),
        TypedDictKeyTypeVerifier("log_type", True, EnumTypeVerifier({log_type.value for log_type in LogType})),
        TypedDictKeyTypeVerifier("reset_on_reload", True, bool),
    ))

    def check(self, fields: LogTypedDict, trace: Trace) -> bool:
        if super().check(fields, trace):
            return True
        try:
            file = self.group.domain.log_directory.joinpath(fields["file_name"])
        except Exception as e:
            trace.exception(e)
            return True
        if self.group.domain.log_directory not in file.parents:
            trace.exception(LogInvalidFileError(self.final, file))
            return True
        return False

    def link_final(self, fields: LogTypedDict) -> None:
        super().link_final(fields)
        self.final.link_log(
            file=self.group.domain.log_directory.joinpath(fields["file_name"]),
            log_type=LogType[fields["log_type"]],
            reset_on_reload=fields["reset_on_reload"],
        )
