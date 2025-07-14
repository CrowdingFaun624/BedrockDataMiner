from typing import Sequence

from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import LogTypedDict
from Component.Field.Field import Field
from Utilities.Exceptions import LogInvalidFileError
from Utilities.Log import Log, LogType
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    EnumTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class LogComponent(Component[Log]):

    class_name = "Log"
    my_capabilities = Capabilities()
    script_referenceable = True
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("file_name", True, str),
        TypedDictKeyTypeVerifier("log_type", True, EnumTypeVerifier({log_type.value for log_type in LogType})),
        TypedDictKeyTypeVerifier("reset_on_reload", True, bool),
        TypedDictKeyTypeVerifier("type", False, str),
    )

    @property
    def assume_used(self) -> bool:
        return True

    __slots__ = (
        "file",
        "file_name",
        "log_type",
        "reset_on_reload",
    )

    def initialize_fields(self, data: LogTypedDict) -> Sequence[Field]:
        self.file_name = data["file_name"]
        self.log_type = LogType[data["log_type"]]
        self.reset_on_reload = data["reset_on_reload"]
        self.domain.log_directory.mkdir(exist_ok=True)
        self.file = self.domain.log_directory.joinpath(self.file_name)
        return ()

    def create_final(self, trace:Trace) -> Log:
        return Log(
            name=self.name,
            file=self.file,
            full_name=self.full_name,
            log_type=self.log_type,
            reset_on_reload=self.reset_on_reload,
        )

    def check(self, trace:Trace) -> None:
        if self.domain.log_directory not in self.file.parents:
            trace.exception(LogInvalidFileError(self.final, self.file))
