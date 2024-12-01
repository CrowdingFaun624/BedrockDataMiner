import inspect
from types import GenericAlias, NoneType, UnionType
from typing import TYPE_CHECKING, Any, Callable, Optional, get_args

import Utilities.Exceptions as Exceptions
import Utilities.Scripts as Scripts

if TYPE_CHECKING:
    import Component.Component as Component


def check(function:Callable, arguments:dict[str,Any], ignore_parameters:set[str], source_component:"Component.Component") -> list[Exception]:
    '''
    Returns a list of Exceptions listing what would go wrong if `function(**arguments)` were to be called.
    :function: The function or Script.
    :arguments: The keyword arguments dictionary to test against `function`.
    :ignore_parameters: Set of parameter names to ignore when checking.
    :source_component: Component to use for error messages.
    '''
    exceptions:list[Exception] = []
    if isinstance(function, Scripts.Script):
        function = function.object
    else:
        function = function
    arg_spec = inspect.getfullargspec(function)
    all_parameters:list[str] = []
    all_parameters.extend(parameter for parameter in arg_spec.args if parameter not in ignore_parameters)
    all_parameters.extend(parameter for parameter in arg_spec.kwonlyargs if parameter not in ignore_parameters)
    defaults:dict[str,Any] = {}
    if arg_spec.defaults is not None:
        defaults.update((key, value) for key, value in zip(reversed(arg_spec.args), arg_spec.defaults) if key not in ignore_parameters)
    if arg_spec.kwonlydefaults is not None:
        defaults.update((key, value) for key, value in arg_spec.kwonlydefaults.items() if key not in ignore_parameters)
    all_parameters_set = set(all_parameters)
    required_parameters = all_parameters_set - defaults.keys()
    exceptions.extend(
        Exceptions.ComponentFunctionMissingArgumentError(source_component, required_parameter)
        for required_parameter in required_parameters
        if required_parameter not in arguments
    )
    if arg_spec.varkw is None:
        exceptions.extend(
            Exceptions.ComponentFunctionUnrecognizedArgumentError(source_component, parameter, argument)
            for parameter, argument in arguments.items()
            if parameter not in all_parameters_set
        )
        kwargs_annotation = None
    else:
        kwargs_annotation:type|None = arg_spec.annotations.get(arg_spec.varkw)
    for parameter, argument in arguments.items():
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
