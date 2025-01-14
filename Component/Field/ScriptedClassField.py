from typing import Callable

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter


class ScriptedClassField[A](Field.Field):

    __slots__ = (
        "class_name",
        "object_class",
        "scripted_objects_function",
    )

    def __init__(self, class_name:str, scripted_objects:Callable[[ScriptImporter.ScriptSetSetSet],ScriptImporter.ScriptSetSet[A]], path: list[str | int]) -> None:
        '''
        :class_name: The name of the scripted object.
        :scripted_objects: A function that returns the desired attribute of the Domain's ScriptSetSetSet.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.class_name:str = class_name
        self.object_class:A
        self.scripted_objects_function = scripted_objects


    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        global_components:dict[str,dict[str,dict[str,"Component.Component"]]],
        functions:"ScriptImporter.ScriptSetSetSet",
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["Component.Component"],list["Component.Component"]]:
        self.object_class = self.scripted_objects_function(functions).get(self.class_name, source_component, self.error_path)
        return [], []
