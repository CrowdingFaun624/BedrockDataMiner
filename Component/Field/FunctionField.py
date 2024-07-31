import inspect
from types import GenericAlias, NoneType, UnionType
from typing import TYPE_CHECKING, Any, Callable, Optional, get_args

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Utilities.Exceptions as Exceptions
import Utilities.Scripts as Scripts

if TYPE_CHECKING:
    import Component.Component as Component

class FunctionField(Field.Field):

    def __init__(self, function_name:str, path:list[str|int]) -> None:
        '''
        :function_name: The name of the function this refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.function_name = function_name
        self.function:Callable|None = None
        self.arguments_to_check:dict[str,Any] = {}
        self.ignore_parameters:set[str] = set()

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["Component.Component"],list["Component.Component"]]:
        function = functions.get(self.function_name)
        if function is None:
            raise Exceptions.ComponentUnrecognizedFunctionError(self.function_name, source_component)
        self.function = function
        return [], []

    def check_arguments(self, arguments:dict[str,Any], ignore_parameters:set[str]|None=None) -> None:
        self.arguments_to_check = arguments
        if ignore_parameters is not None:
            self.ignore_parameters = ignore_parameters

    def get_function(self) -> Callable:
        '''
        Returns the function this Field refers to.
        Can only be called after `set_field`.
        '''
        if self.function is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.get_function, self)
        return self.function

    def check(self, source_component: Component.Component) -> list[Exception]:
        exceptions = super().check(source_component)
        if isinstance(self.function, Scripts.LuaScript):
            return exceptions # Lua functions cannot be inspected.
        elif isinstance(self.function, Scripts.PythonScript):
            function = self.function.object
        else:
            function = self.function
        arg_spec = inspect.getfullargspec(function)
        all_parameters:list[str] = []
        all_parameters.extend(parameter for parameter in arg_spec.args if parameter not in self.ignore_parameters)
        all_parameters.extend(parameter for parameter in arg_spec.kwonlyargs if parameter not in self.ignore_parameters)
        defaults:dict[str,Any] = {}
        if arg_spec.defaults is not None:
            defaults.update((key, value) for key, value in zip(reversed(arg_spec.args), arg_spec.defaults) if key not in self.ignore_parameters)
        if arg_spec.kwonlydefaults is not None:
            defaults.update((key, value) for key, value in arg_spec.kwonlydefaults.items() if key not in self.ignore_parameters)
        all_parameters_set = set(all_parameters)
        required_parameters = all_parameters_set - defaults.keys()
        exceptions.extend(
            Exceptions.ComponentFunctionMissingArgumentError(source_component, required_parameter)
            for required_parameter in required_parameters
            if required_parameter not in self.arguments_to_check
        )
        if arg_spec.varkw is None:
            exceptions.extend(
                Exceptions.ComponentFunctionUnrecognizedArgumentError(source_component, parameter, argument)
                for parameter, argument in self.arguments_to_check.items()
                if parameter not in all_parameters_set
            )
            kwargs_annotation = None
        else:
            kwargs_annotation:type|None = arg_spec.annotations.get(arg_spec.varkw)
        for parameter, argument in self.arguments_to_check.items():
            annotation:type|UnionType|GenericAlias|None = arg_spec.annotations.get(parameter, kwargs_annotation)
            allowed_types:tuple[Any,...]
            match annotation:
                case NoneType():
                    argument_good = True
                    allowed_types = ()
                case GenericAlias():
                    argument_good = isinstance(argument, annotation.__origin__)
                    allowed_types = (annotation.__origin__,)
                case type():
                    argument_good = isinstance(argument, annotation)
                    allowed_types = (annotation,)
                case UnionType() | Optional():
                    try:
                        argument_good = isinstance(argument, annotation)
                    except TypeError: # Some UnionTypes can be filled with gobbledygook like strings that make this thing explode.
                        argument_good = True
                    allowed_types = get_args(annotation)
                case Any():
                    argument_good = True
                    allowed_types = (Any,)
                case _:
                    # you can technically put anything in annotations
                    argument_good = True
                    allowed_types = ()
            if not argument_good:
                exceptions.append(Exceptions.ComponentFunctionArgumentTypeError(source_component, parameter, argument, type(argument), allowed_types))
            
        return exceptions
