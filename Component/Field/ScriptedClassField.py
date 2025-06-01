from typing import Callable, Sequence

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Field.FieldContainer as FieldContainer
import Component.ScriptImporter as ScriptImporter
import Utilities.Trace as Trace


class ScriptedClassField[A](Field.Field):

    __slots__ = (
        "class_name",
        "object_class",
        "scripted_objects_function",
    )

    def __init__(self, class_name:str, scripted_objects:Callable[[ScriptImporter.ScriptSetSetSet],ScriptImporter.ScriptSetSet[A]], path: tuple[str,...]) -> None:
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
        trace:Trace.Trace,
    ) -> tuple[Sequence["Component.Component"],Sequence["Component.Component"]]:
        with trace.enter_keys(self.trace_path, self.class_name):
            self.object_class = self.scripted_objects_function(functions).get(self.class_name, source_component)
            return (), ()
        return (), ()

class OptionalScriptedClassField[A, B](FieldContainer.FieldContainer):

    __slots__ = (
        "default",
        "scripted_class_field",
    )

    def __init__(self, class_name:str|None, scripted_objects:Callable[[ScriptImporter.ScriptSetSetSet],ScriptImporter.ScriptSetSet[A]], path: tuple[str,...], *, default:B=None) -> None:
        '''
        :class_name: The name of the scripted object or None.
        :scripted_objects: A function that returns the desired attribute of the Domain's ScriptSetSetSet.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        self.scripted_class_field:ScriptedClassField|None
        self.default = default
        if class_name is None:
            self.scripted_class_field = None
            super().__init__([], path)
        else:
            self.scripted_class_field = ScriptedClassField(class_name, scripted_objects, path)
            super().__init__([self.scripted_class_field], path)

    @property
    def object_class(self) -> A|B:
        return self.default if self.scripted_class_field is None else self.scripted_class_field.object_class

    @property
    def exists(self) -> bool:
        return self.scripted_class_field is not None
