from pathlib import Path
from typing import Iterable

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.ImporterEnvironment as ImporterEnvironment
import Component.Structure.BaseComponent as BaseComponent
import Structure.StructureBase as StructureBase
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager


class StructureImporterEnvironment(ImporterEnvironment.ImporterEnvironment[StructureBase.StructureBase]):

    __slots__ = ()

    def get_imports(self, components:dict[str,Component.Component], all_components:dict[str,dict[str,Component.Component]], name:str) -> dict[str,dict[str, Component.Component]]:
        output:dict[str,dict[str,Component.Component]] = {}
        output["versions"] = all_components["versions"]
        output["structure_tags"] = all_components["structure_tags"]
        imports:list[ComponentTyping.ImportTypedDict]|None = None
        for component in components.values():
            if isinstance(component, BaseComponent.BaseComponent):
                imports = component.imports
                break
        if imports is None: return output
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

    def get_base_component(self, components:dict[str,Component.Component], name:str) -> BaseComponent.BaseComponent:
        base_components:dict[str,BaseComponent.BaseComponent] = {
            component_name: component
            for component_name, component in components.items()
            if isinstance(component, BaseComponent.BaseComponent)
        }
        if len(base_components) != 1:
            raise Exceptions.BaseComponentCountError(name, list(base_components.values()))
        return next(iter(base_components.values()))

    def get_output(self, components: dict[str,Component.Component], name: str) -> StructureBase.StructureBase:
        return self.get_base_component(components, name).get_final()

    def get_assumed_used_components(self, components: dict[str, Component.Component], name:str) -> Iterable[Component.Component]:
        return [self.get_base_component(components, name)]

    def get_from_directory(self, directory_path:Path) -> Iterable[Path]:
        for subpath in directory_path.iterdir():
            if subpath.is_file():
                yield subpath
            else:
                yield from self.get_from_directory(subpath)

    def get_component_files(self) -> Iterable[Path]:
        yield from self.get_from_directory(FileManager.STRUCTURES_DIRECTORY)

    def get_component_group_name(self, file_path:Path) -> str:
        return "structures/" + file_path.relative_to(FileManager.STRUCTURES_DIRECTORY).as_posix().removesuffix(file_path.suffix)
