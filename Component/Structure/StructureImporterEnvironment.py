from pathlib import Path
from typing import Iterable

from Component.Component import Component
from Component.ImporterEnvironment import ImporterEnvironment
from Component.Structure.StructureBaseComponent import StructureBaseComponent
from Structure.StructureBase import StructureBase
from Utilities.Exceptions import BaseComponentCountError
from Utilities.Trace import Trace


class StructureImporterEnvironment(ImporterEnvironment[StructureBase]):

    __slots__ = ()

    def get_base_component(self, components:dict[str,Component], name:str) -> StructureBaseComponent:
        base_components:dict[str,StructureBaseComponent] = {
            component_name: component
            for component_name, component in components.items()
            if isinstance(component, StructureBaseComponent)
        }
        if len(base_components) != 1:
            raise BaseComponentCountError(name, list(base_components.values()))
        return next(iter(base_components.values()))

    def get_output(self, components: dict[str,Component], name: str, trace:Trace) -> StructureBase:
        return self.get_base_component(components, name).final

    def get_assumed_used_components(self, components: dict[str, Component], name:str, trace:Trace) -> Iterable[Component]:
        with trace.enter(self, name, ...):
            return (self.get_base_component(components, name),)
        return ()

    def get_from_directory(self, directory_path:Path) -> Iterable[Path]:
        for subpath in directory_path.iterdir():
            if subpath.is_file():
                yield subpath
            else:
                yield from self.get_from_directory(subpath)

    def get_component_files(self) -> Iterable[Path]:
        if self.domain.structures_directory.exists():
            yield from self.get_from_directory(self.domain.structures_directory)

    def get_component_group_name(self, file_path:Path) -> str:
        return "structures/" + file_path.relative_to(self.domain.structures_directory).as_posix().removesuffix(file_path.suffix)
