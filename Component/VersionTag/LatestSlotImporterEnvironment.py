from typing import Iterable

from pathlib2 import Path

from Component.Component import Component
import Component.ImporterEnvironment as ImporterEnvironment
import Component.VersionTag.LatestSlotComponent as LatestSlotComponent
import Utilities.FileManager as FileManager


class LatestSlotImporterEnvironment(ImporterEnvironment.ImporterEnvironment[list[str]]):
    
    assume_type=LatestSlotComponent.LatestSlotComponent.class_name
    
    def get_component_files(self) -> Iterable[Path]:
        return [FileManager.LATEST_SLOTS_FILE]

    def get_output(self, components: dict[str, Component], name: str) -> tuple[list[str], list[Component]]:
        return [component.get_final() for component in components.values()], []

    def get_component_group_name(self, file_path: Path) -> str:
        return "latest_slots"
