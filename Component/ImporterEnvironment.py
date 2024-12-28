from pathlib import Path
from typing import Any, Iterable

import Component.Component as Component


class ImporterEnvironment[a]():
    "Abstract class for configuring how Component.Importer imports Components."

    assume_type:str|None = None
    "If the type key of a Component is not present and assume_type is not None, it will use the value of assume_type as the type key."

    single_component:bool = False
    "If the Component group has a singular, unnamed Component or multiple Components."

    def get_imports(self, components:dict[str,Component.Component], all_components:dict[str,dict[str,Component.Component]], name:str) -> dict[str,dict[str,Component.Component]]:
        '''
        Given the current Component group and all other Component groups.
        Returns a dict with keys of the name of the Component group imported from and values of dictionaries of Components with their names.
        :components: The Components in the current Component group.
        :all_components: The Components in each Component Group.
        :name: The name of the current Component group.
        '''
        return {}

    def get_output(self, components:dict[str,Component.Component], name:str) -> a:
        '''
        Given the Component group, return the intended output from the Component group.
        By default, returns the finals of all Components.
        :components: The Components in the current Component group.
        :name: The name of the current Component group.
        '''
        output = {component_name: component.get_final() for component_name, component in components.items()}
        if self.single_component:
            return output[""]
        else:
            return output # type: ignore

    def get_component_files(self) -> Iterable[Path]:
        '''
        Returns a list of Paths that this ImporterEnvironment uses.
        '''
        ...

    def get_assumed_used_components(self, components:dict[str,Component.Component], name:str) -> Iterable[Component.Component]:
        '''
        Returns the Components that are marked as used.
        :components: All Components in his Component group.
        '''
        if self.single_component:
            return components.values()
        else:
            return ()

    def finalize(self, output:a, other_outputs:dict[str,Any]) -> None:
        '''
        Run any final actions on the output.
        :output: The output that `get_output` returned.
        :other_outputs: The outputs of all Component groups.
        '''
        ...

    def check(self, output:a, other_outputs:dict[str,Any]) -> list[Exception]:
        '''
        Make sure that this Component's types are all in order; no error could occur.
        :output: The output that `get_output` returned.
        :other_outputs: The outputs of all Component groups.
        '''
        return []

    def get_component_group_name(self, file_path:Path) -> str:
        '''
        Returns the name of the Component group based on the file path.
        :file_path: The file path of this Component group.
        '''
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {id(self)}>"
