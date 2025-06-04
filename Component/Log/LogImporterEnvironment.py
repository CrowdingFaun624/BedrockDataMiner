from pathlib import Path
from typing import Iterable

from Component.Component import Component
from Component.ImporterEnvironment import ImporterEnvironment
from Component.Log.LogComponent import LogComponent
from Utilities.Log import Log
from Utilities.Trace import Trace


class LogImporterEnvironment(ImporterEnvironment[dict[str,Log]]):

    assume_type = LogComponent.class_name

    __slots__ = ()

    def get_component_files(self) -> Iterable[Path]:
        return (self.domain.logs_file,)

    def get_assumed_used_components(self, components: dict[str, Component], name: str, trace:Trace) -> Iterable[Component]:
        with trace.enter(self, name, ...):
            return components.values()
        return ()

    def get_component_group_name(self, file_path: Path) -> str:
        return "logs"
