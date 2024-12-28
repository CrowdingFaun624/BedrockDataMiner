from pathlib import Path
from typing import Iterable

import Component.Component as Component
import Component.ImporterEnvironment as ImporterEnvironment
import Component.Version.VersionFileTypeComponent as VersionFileTypeComponent
import Utilities.FileManager as FileManager
import Version.VersionFileType as VersionFileType


class VersionFileTypeImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,VersionFileType.VersionFileType]]):

    assume_type = VersionFileTypeComponent.VersionFileTypeComponent.class_name

    __slots__ = ()

    def get_imports(self, components:dict[str,Component.Component], all_components:dict[str,dict[str,Component.Component]], name:str) -> dict[str,dict[str,Component.Component]]:
        return {"accessor_types": all_components["accessor_types"]}

    def get_component_files(self) -> Iterable[Path]:
        return [FileManager.VERSION_FILE_TYPES_FILE]

    def get_component_group_name(self, file_path: Path) -> str:
        return "version_file_types"
