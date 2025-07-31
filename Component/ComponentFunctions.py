from typing import Any, Callable

from Domain.Domains import get_domain_from_module
from Utilities.Scripts import BuiltInScript, UserScript
from Utilities.TypeVerifier import TypedDictTypeVerifier

EMPTY_TYPE_VERIFIER = TypedDictTypeVerifier()

def component_function[T:Callable](*, type_verifier:TypedDictTypeVerifier|None=None, no_arguments:bool=False, opens_files:bool=False) -> Callable[[T], T]:
    '''
    Use as a decorator on an object that should be made available to Components.

    :type_verifier: The keyword arguments on a function.
    :no_arguments: If True, sets `type_verifier` to an empty TypedDictTypeVerifier.
    :opens_files: Set to True if this function opens Files and is used in a Function by a Structure.
    '''
    if no_arguments:
        type_verifier = EMPTY_TYPE_VERIFIER
    def comp_func(func:T) -> T:
        domain = get_domain_from_module(func.__module__)
        relative_name:str = func.__module__.replace(".", "/").removeprefix(f"_domains/{domain.name}/scripts/")
        item_name:str = func.__name__
        domain.scripts.scripts[(relative_name, item_name)] = UserScript(relative_name, item_name, func, domain, type_verifier=type_verifier, opens_files=opens_files)
        return func
    return comp_func

BUILT_INS:dict[str,Any] = {}

def register_builtin[T:Callable](*, type_verifier:TypedDictTypeVerifier|None=None, no_arguments:bool=False, opens_files:bool=False) -> Callable[[T],T]:
    if no_arguments:
        type_verifier = EMPTY_TYPE_VERIFIER
    def comp_func(func:T) -> T:
        item_name:str = func.__name__
        BUILT_INS[item_name] = BuiltInScript(item_name, func, type_verifier=type_verifier, opens_files=opens_files)
        return func
    return comp_func
