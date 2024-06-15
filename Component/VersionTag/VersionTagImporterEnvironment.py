from typing import Iterable

from pathlib2 import Path

import Component.Component as Component
import Component.ImporterEnvironment as ImporterEnvironment
import Component.VersionTag.VersionTagComponent as VersionTagComponent
import Utilities.FileManager as FileManager
import Version.VersionTag.VersionTag as VersionTag


class VersionTagImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,VersionTag.VersionTag]]):
    
    assume_type = VersionTagComponent.VersionTagComponent.class_name
    
    def get_imports(self, components:dict[str,Component.Component], all_components:dict[str,dict[str,Component.Component]], name:str) -> dict[str,dict[str,Component.Component]]:
        return {"versions": all_components["versions"], "latest_slots": all_components["latest_slots"]}

    def get_component_files(self) -> Iterable[Path]:
        return [FileManager.VERSION_TAGS_FILE]

    def get_component_group_name(self, file_path: Path) -> str:
        return "version_tags"
