from typing import Sequence

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Utilities.Exceptions as Exceptions
import Utilities.Log as Log
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier


class LogComponent(Component.Component[Log.Log]):

    class_name = "Log"
    my_capabilities = Capabilities.Capabilities()
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("file_name", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("log_type", True, TypeVerifier.EnumTypeVerifier({log_type.value for log_type in Log.LogType})),
        TypeVerifier.TypedDictKeyTypeVerifier("reset_on_reload", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "file",
        "file_name",
        "log_type",
        "reset_on_reload",
    )

    def initialize_fields(self, data: ComponentTyping.LogTypedDict) -> Sequence[Field.Field]:
        self.file_name = data["file_name"]
        self.log_type = Log.LogType[data["log_type"]]
        self.reset_on_reload = data["reset_on_reload"]
        self.domain.log_directory.mkdir(exist_ok=True)
        self.file = self.domain.log_directory.joinpath(self.file_name)
        return ()

    def create_final(self, trace:Trace.Trace) -> Log.Log:
        return Log.Log(
            name=self.name,
            file=self.file,
            log_type=self.log_type,
            reset_on_reload=self.reset_on_reload,
        )

    def check(self, trace:Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().check(trace)
            if self.domain.log_directory not in self.file.parents:
                trace.exception(Exceptions.LogInvalidFileError(self.final, self.file))
