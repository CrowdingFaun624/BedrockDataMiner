from pathlib import Path
from typing import Iterable

import Component.Accessor.AccessorTypeComponent as AccessorTypeComponent
import Component.ImporterEnvironment as ImporterEnvironment
import Downloader.AccessorType as AccessorType


class AccessorTypeImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,AccessorType.AccessorType]]):

    assume_type = AccessorTypeComponent.AccessorTypeComponent.class_name

    __slots__ = ()

    def get_component_files(self) -> Iterable[Path]:
        return (self.domain.accessor_types_file,)

    def get_component_group_name(self, file_path: Path) -> str:
        return "accessor_types"
