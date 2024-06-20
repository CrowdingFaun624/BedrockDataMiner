from typing import Iterable

from pathlib2 import Path

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.ImporterEnvironment as ImporterEnvironment
import Component.Structure.BaseComponent as BaseComponent
import Structure.StructureBase as StructureBase
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager


class StructureImporterEnvironment(ImporterEnvironment.ImporterEnvironment[StructureBase.StructureBase]):

    def get_imports(self, components:dict[str,Component.Component], all_components:dict[str,dict[str,Component.Component]], name:str) -> dict[str,dict[str, Component.Component]]:
        output:dict[str,dict[str,Component.Component]] = {}
        imports:list[ComponentTyping.ImportTypedDict]|None = None
        for component in components.values():
            if isinstance(component, BaseComponent.BaseComponent):
                imports = component.imports
                break
        if imports is None: return {}
        for import_data in imports:
            import_from = import_data["from"]
            if import_from == name:
                raise Exceptions.ComponentImporterCircularImportError([name], "(attempted to self-import)")
            output[import_from] = {}
            for import_component_data in import_data["components"]:
                import_component_name = import_component_data["component"]
                import_component_as = import_component_data.get("as", import_component_name)
                output[import_from][import_component_as] = all_components[import_from][import_component_name]
        return output

    def get_output(self, components: dict[str,Component.Component], name: str) -> tuple[StructureBase.StructureBase,list[Component.Component]]:
        base_components:dict[str,BaseComponent.BaseComponent] = {
            component_name: component
            for component_name, component in components.items()
            if isinstance(component, BaseComponent.BaseComponent)
        }
        if len(base_components) != 1:
            raise Exceptions.BaseComponentCountError(name, len(base_components), "(names: [%s])" % (", ".join(base_components.keys()),))
        base_component = next(iter(base_components.values()))
        unused_components = self.get_unused_components([base_component], components)
        return base_component.get_final(), unused_components

    def get_component_files(self) -> Iterable[Path]:
        return FileManager.STRUCTURES_DIRECTORY.iterdir()

    def get_component_group_name(self, file_path:Path) -> str:
        return "structures/" + file_path.stem
