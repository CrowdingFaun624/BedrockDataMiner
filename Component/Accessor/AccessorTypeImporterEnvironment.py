from typing import Iterable

from pathlib2 import Path

import Component.ImporterEnvironment as ImporterEnvironment
import Component.Accessor.AccessorTypeComponent as AccessorTypeComponent
import Downloader.AccessorType as AccessorType
import Utilities.FileManager as FileManager
from Utilities.FunctionCaller import WaitValue


class AccessorTypeImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,WaitValue[AccessorType.AccessorType]]]):

    assume_type = AccessorTypeComponent.AccessorTypeComponent.class_name

    def get_component_files(self) -> Iterable[Path]:
        return [FileManager.ACCESSOR_TYPES_FILE]

    def get_component_group_name(self, file_path: Path) -> str:
        return "accessor_types"
