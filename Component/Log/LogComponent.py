import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.Log as Log
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class LogComponent(Component.Component[Log.Log]):

    class_name = "Log"
    class_name_article = "a Log"
    my_capabilities = Capabilities.Capabilities(is_log=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("file_name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("log_type", "a str", True, TypeVerifier.EnumTypeVerifier({log_type.value for log_type in Log.LogType})),
        TypeVerifier.TypedDictKeyTypeVerifier("reset_on_reload", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    __slots__ = (
        "file",
        "file_name",
        "log_type",
        "reset_on_reload",
    )

    def __init__(self, data: ComponentTyping.LogTypedDict, name: str, component_group: str, index: int | None) -> None:
        super().__init__(data, name, component_group, index)

        self.file_name = data["file_name"]
        self.log_type = Log.LogType[data["log_type"]]
        self.reset_on_reload = data["reset_on_reload"]

        self.file = FileManager.LOG_DIRECTORY.joinpath(self.file_name)

    def create_final(self) -> None:
        super().create_final()
        self.final = Log.Log(
            name=self.name,
            file=self.file,
            log_type=self.log_type,
            reset_on_reload=self.reset_on_reload,
        )

    def check(self) -> list[Exception]:
        exceptions = super().check()
        if self.file is FileManager.LOGS_FILE or FileManager.LOG_DIRECTORY not in self.file.parents:
            exceptions.append(Exceptions.LogInvalidFileError(self.get_final(), self.file))
        return exceptions
