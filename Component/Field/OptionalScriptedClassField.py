from typing import Callable, Sequence

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter


class OptionalScriptedClassField[A, B](Field.Field):

    __slots__ = (
        "class_name",
        "default",
        "object_class",
        "scripted_objects_function",
    )

    def __init__(self, class_name:str|None, scripted_objects:Callable[[ScriptImporter.ScriptSetSetSet],ScriptImporter.ScriptSetSet[A]], path: tuple[str,...], *, default:B=None) -> None:
        '''
        :class_name: The name of the scripted object.
        :scripted_objects: A function that returns the desired attribute of the Domain's ScriptSetSetSet.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.class_name:str|None = class_name
        self.default:B = default
        self.object_class:A|B
        self.scripted_objects_function = scripted_objects


    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        global_components:dict[str,dict[str,dict[str,"Component.Component"]]],
        functions:"ScriptImporter.ScriptSetSetSet",
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[Sequence["Component.Component"],Sequence["Component.Component"]]:
        self.object_class = self.scripted_objects_function(functions).get(self.class_name, source_component, self.error_path) if self.class_name is not None else self.default
        return (), ()

    @property
    def exists(self) -> bool:
        return self.class_name is not None
