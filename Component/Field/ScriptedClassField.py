from typing import TYPE_CHECKING, Callable, Sequence

from Component.Component import Component
from Component.ComponentTyping import CreateComponentFunction
from Component.Field.Field import Field
from Component.Field.FieldContainer import FieldContainer
from Component.ScriptImporter import ScriptSetSet, ScriptSetSetSet
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Group import Group

class ScriptedClassField[A](Field):

    __slots__ = (
        "class_name",
        "object_class",
        "scripted_objects_function",
    )

    def __init__(self, class_name:str, scripted_objects:Callable[[ScriptSetSetSet],ScriptSetSet[A]], path: tuple[str,...]) -> None:
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
        source_component:"Component",
        local_group:"Group",
        global_groups:dict[str,dict[str,"Group"]],
        functions:"ScriptSetSetSet",
        create_component_function:CreateComponentFunction,
        trace:Trace,
    ) -> tuple[Sequence["Component"],Sequence["Component"]]:
        with trace.enter_keys(self.trace_path, self.class_name):
            self.object_class = self.scripted_objects_function(functions).get(self.class_name, source_component)
            return (), ()
        return (), ()

class OptionalScriptedClassField[A, B](FieldContainer):

    __slots__ = (
        "default",
        "scripted_class_field",
    )

    def __init__(self, class_name:str|None, scripted_objects:Callable[[ScriptSetSetSet],ScriptSetSet[A]], path: tuple[str,...], *, default:B=None) -> None:
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
