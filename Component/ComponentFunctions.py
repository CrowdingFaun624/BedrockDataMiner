from typing import Callable

from Domain.Domains import get_domain_from_module
from Utilities.Scripts import Script
from Utilities.TypeVerifier import TypedDictTypeVerifier

function_type_verifiers:dict[Callable, TypedDictTypeVerifier] = {}

EMPTY_TYPE_VERIFIER = TypedDictTypeVerifier()

def component_function[T:Callable](*, type_verifier:TypedDictTypeVerifier|None=None, no_arguments:bool=False) -> Callable[[T], T]:
    '''
    Use as a decorator on an object that should be made available to Components.

    :type_verifier: The keyword arguments on a function.
    :no_arguments: If True, sets `type_verifier` to an empty TypedDictTypeVerifier.
    '''
    if no_arguments:
        type_verifier = EMPTY_TYPE_VERIFIER
    def comp_func(func:T) -> T:
        domain = get_domain_from_module(func.__module__)
        relative_name:str = func.__module__.replace(".", "/").removeprefix(f"_domains/{domain.name}/scripts/")
        item_name:str = func.__name__
        if type_verifier is not None:
            function_type_verifiers[func] = type_verifier
        domain.scripts.scripts[(relative_name, item_name)] = Script(relative_name, item_name, func, domain)
        return func
    return comp_func
