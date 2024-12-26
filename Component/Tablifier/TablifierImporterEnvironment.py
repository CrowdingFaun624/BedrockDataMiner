from pathlib import Path
from typing import Iterable

import Component.Component as Component
import Component.ImporterEnvironment as ImporterEnvironment
import Tablifier.Tablifier as Tablifier
import Utilities.FileManager as FileManager


class TablifierImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,Tablifier.Tablifier]]):

    assume_type = "Tablifier"

    def get_imports(self, components: dict[str, Component.Component], all_components: dict[str, dict[str, Component.Component]], name: str) -> dict[str, dict[str, Component.Component]]:
        output:dict[str, dict[str, Component.Component]] = {}
        output["dataminer_collections"] = all_components["dataminer_collections"]
        output.update((component_group_name, components) for component_group_name, components in all_components.items() if component_group_name.startswith("structures/"))
        return output

    def get_component_files(self) -> Iterable[Path]:
        return (FileManager.TABLIFIERS_FILE,)

    def get_assumed_used_components(self, components: dict[str, Component.Component], name:str) -> Iterable[Component.Component]:
        return components.values()

    def get_component_group_name(self, file_path: Path) -> str:
        return "tablifiers"
