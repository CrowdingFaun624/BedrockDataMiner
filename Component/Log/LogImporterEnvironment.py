from pathlib import Path
from typing import Iterable

import Component.Component as Component
import Component.ImporterEnvironment as ImporterEnvironment
import Component.Log.LogComponent as LogComponent
import Utilities.Log as Log


class LogImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,Log.Log]]):

    assume_type = LogComponent.LogComponent.class_name

    __slots__ = ()

    def get_component_files(self) -> Iterable[Path]:
        return (self.domain.logs_file,)

    def get_assumed_used_components(self, components: dict[str, Component.Component], name: str) -> Iterable[Component.Component]:
        return components.values()

    def get_component_group_name(self, file_path: Path) -> str:
        return "logs"
