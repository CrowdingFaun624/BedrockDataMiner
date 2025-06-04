from pathlib import Path
from types import EllipsisType
from typing import Iterable

from Component.Component import Component
from Component.ImporterEnvironment import ImporterEnvironment
from Component.VersionTag.LatestSlotComponent import LatestSlotComponent
from Utilities.Trace import Trace


class LatestSlotImporterEnvironment(ImporterEnvironment[list[str]]):

    assume_type=LatestSlotComponent.class_name

    __slots__ = ()

    def get_component_files(self) -> Iterable[Path]:
        return (self.domain.latest_slots_file,)

    def get_output(self, components: dict[str, Component], name: str, trace:Trace) -> list[str]|EllipsisType:
        with trace.enter(self, name, ...):
            return [component.final for component in components.values()]
        return ...

    def get_component_group_name(self, file_path: Path) -> str:
        return "latest_slots"
