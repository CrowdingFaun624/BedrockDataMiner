from typing import Any, Generic, Iterable, TypeVar

from pathlib2 import Path

import Component.Component as Component

a = TypeVar("a")

class ImporterEnvironment(Generic[a]):
    "Abstract class for configuring how Component.Importer imports Components."

    assume_type:str|None = None
    "If the type key of a Component is not present and assume_type is not None, it will use the value of assume_type as the type key."

    def get_imports(self, components:dict[str,Component.Component], all_components:dict[str,dict[str,Component.Component]], name:str) -> dict[str,dict[str,Component.Component]]:
        '''
        Given the current Component group and all other Component groups.
        Returns a dict with keys of the name of the Component group imported from and values of dictionaries of Components with their names.
        :components: The Components in the current Component group.
        :all_components: The Components in each Component Group.
        :name: The name of the current Component group.
        '''
        return {}

    def get_output(self, components:dict[str,Component.Component], name:str) -> tuple[a,list[Component.Component]]:
        '''
        Given the Component group, return the intended output from the Component group and a list of unused Components.
        By default, returns the finals of all Components.
        :components: The Components in the current Component group.
        :name: The name of the current Component group.
        '''
        output = {component_name: component.get_final() for component_name, component in components.items()}
        return output, [] # type: ignore

    def get_component_files(self) -> Iterable[Path]:
        '''
        Returns a list of Paths that this ImporterEnvironment uses.
        '''
        ...

    def get_unused_components(self, start_components:list[Component.Component], components:dict[str,Component.Component]) -> list[Component.Component]:
        '''
        Returns a list of unused Components.
        :start_components: Components that are used and are used to determine which are not used.
        :components: All Components in this Component group.
        '''
        visited_nodes:set[Component.Component] = set()
        unvisited_nodes = start_components
        while len(unvisited_nodes) > 0:
            unvisited_node = unvisited_nodes.pop()
            if unvisited_node in visited_nodes: continue
            for neighbor in unvisited_node.links_to_other_components:
                if neighbor in visited_nodes:
                    continue
                else:
                    unvisited_nodes.append(neighbor)
            visited_nodes.add(unvisited_node)
        output:list[Component.Component] = []
        for component in components.values():
            if component not in visited_nodes: output.append(component)
        return output
    
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
        return "<%s %i>" % (self.__class__.__name__, id(self))
