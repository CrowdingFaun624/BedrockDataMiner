from pathlib import Path
from typing import Iterable

import Component.Component as Component
import Component.ImporterEnvironment as ImporterEnvironment
import Component.VersionTag.LatestSlotComponent as LatestSlotComponent


class LatestSlotImporterEnvironment(ImporterEnvironment.ImporterEnvironment[list[str]]):

    assume_type=LatestSlotComponent.LatestSlotComponent.class_name

    __slots__ = ()

    def get_component_files(self) -> Iterable[Path]:
        return (self.domain.latest_slots_file,)

    def get_output(self, components: dict[str, Component.Component], name: str) -> list[str]:
        return [component.final for component in components.values()]

    def get_component_group_name(self, file_path: Path) -> str:
        return "latest_slots"
