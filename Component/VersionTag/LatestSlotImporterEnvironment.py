from pathlib import Path
from types import EllipsisType
from typing import Iterable

import Component.Component as Component
import Component.ImporterEnvironment as ImporterEnvironment
import Component.VersionTag.LatestSlotComponent as LatestSlotComponent
import Utilities.Trace as Trace


class LatestSlotImporterEnvironment(ImporterEnvironment.ImporterEnvironment[list[str]]):

    assume_type=LatestSlotComponent.LatestSlotComponent.class_name

    __slots__ = ()

    def get_component_files(self) -> Iterable[Path]:
        return (self.domain.latest_slots_file,)

    def get_output(self, components: dict[str, Component.Component], name: str, trace:Trace.Trace) -> list[str]|EllipsisType:
        with trace.enter(self, name, ...):
            return [component.final for component in components.values()]
        return ...

    def get_component_group_name(self, file_path: Path) -> str:
        return "latest_slots"
