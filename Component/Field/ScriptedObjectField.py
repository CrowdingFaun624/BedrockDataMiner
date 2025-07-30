from types import EllipsisType
from typing import TYPE_CHECKING, Any, Callable, Mapping, Sequence, TypeIs

from Component.Component import Component
from Component.ComponentTyping import CreateComponentFunction
from Component.Field.Field import Field
from Component.Field.FieldContainer import FieldContainer
from Component.ScriptImporter import ScriptSetSet
from Utilities.Scripts import Script
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Group import Group

class ScriptedObjectField[A](Field):

    __slots__ = (
        "instance",
        "object",
        "object_name",
        "script",
        "subclass",
        "type_name",
        "verify_function",
    )

    def __init__(self, object_name:str, path: tuple[str,...], cumulative_path:tuple[str,...]|None=None, verify_function:Callable[[Any],TypeIs[A]]|None=None, instance:type[A]|None=None, subclass:A|None=None, type_name:str|None=None) -> None:
        '''
        :object_name: The name of the scripted object.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        :verify_function: An optional function used to verify that the referenced object is valid.
        :instance: An optional type to verify that the referenced object is an instance of it.
        :subclass: An optional type to verify that the referenced object is a subclass of it.
        :type_name: A string representing the types given by `verify_function`, `instance`, and/or `subclass`.
        '''
        super().__init__(path, cumulative_path)
        self.object_name:str = object_name
        self.object:A
        self.verify_function = verify_function
        self.instance = instance
        self.subclass = subclass
        self.type_name = type_name

    def set_field(
        self,
        source_component:"Component",
        local_group:"Group",
        global_groups:Mapping[str,Mapping[str,"Group"]],
        functions:"ScriptSetSet",
        create_component_function:CreateComponentFunction,
        trace:Trace,
    ) -> tuple[Sequence["Component"],Sequence["Component"]]:
        with trace.enter_keys(self.trace_path, self.object_name):
            script:Script[A]|EllipsisType = functions.get(self.object_name, source_component.domain, trace, self.verify_function, self.instance, self.subclass, self.type_name)
            if script is not ...:
                self.object = script.object
                self.script = script
            return (), ()
        return (), ()

class OptionalScriptedObjectField[A, B](FieldContainer):

    __slots__ = (
        "default",
        "scripted_class_field",
    )

    def __init__(self, object_name:str|None, path: tuple[str,...], cumulative_path:tuple[str,...]|None=None, default:B=None, verify_function:Callable[[Any],TypeIs[A]]|None=None, instance:type[A]|None=None, subclass:A|None=None, type_name:str|None=None) -> None:
        '''
        :object_name: The name of the scripted object.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        :default: The object to return if `object_name` is None.
        :verify_function: An optional function used to verify that the referenced object is valid.
        :instance: An optional type to verify that the referenced object is an instance of it.
        :subclass: An optional type to verify that the referenced object is a subclass of it.
        :type_name: A string representing the types given by `verify_function`, `instance`, and/or `subclass`.
        '''
        self.scripted_class_field:ScriptedObjectField|None
        self.default = default
        if object_name is None:
            self.scripted_class_field = None
            super().__init__([], path, cumulative_path)
        else:
            self.scripted_class_field = ScriptedObjectField(object_name, path, cumulative_path, verify_function, instance, subclass, type_name)
            super().__init__([self.scripted_class_field], path, cumulative_path)

    @property
    def object(self) -> A|B:
        return self.default if self.scripted_class_field is None else self.scripted_class_field.object

    @property
    def script(self) -> Script[A]|None:
        return None if self.scripted_class_field is None else self.scripted_class_field.script

    @property
    def exists(self) -> bool:
        return self.scripted_class_field is not None
