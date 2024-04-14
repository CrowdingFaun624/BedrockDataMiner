from typing import Any, Callable, Generic, TypeVar

import Utilities.TypeVerifier as TypeVerifier

T = TypeVar("T") # I love type hinting

class FunctionCaller(Generic[T]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("target", "a Callable", True, Callable),
        TypeVerifier.TypedDictKeyTypeVerifier("args", "a list or None", True, (list, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("kwargs", "a dict or None", True, (dict, type(None))),
    )

    def __init__(self, target:Callable[..., T], args:list[Any]|None=None, kwargs:dict[str,Any]|None=None) -> None:
        self.type_verifier.base_verify({"target": target, "args": args, "kwargs": kwargs})

        self.target = target
        self.args = [] if args is None else args
        self.kwargs = {} if kwargs is None else kwargs

    def __call__(self) -> T:
        return self.target(*self.args, **self.kwargs)

    def __repr__(self) -> str:
        return "<%s %s>" % (self.__class__.__name__, self.target)

class WaitValue(Generic[T]):
    '''Does not call the FunctionCaller until `get` is called. It then stores the output of the FunctionCaller for future calls of `get`.'''

    def __init__(self, caller:FunctionCaller[T]|Callable[[],T]) -> None:
        if not isinstance(caller, (FunctionCaller, Callable)):
            raise TypeError("`caller` is not a FunctionCaller or Callable!")
        self.caller = caller
        self.has_called = False
        self.value = None

    def get(self) -> T:
        if not self.has_called:
            self.has_called = True
            self.value = self.caller()
        return self.value

    def set(self, value:T) -> None:
        if self.value is None:
            self.has_called = True
        self.value = value

    def __repr__(self) -> str:
        return "<%s %s %s>" % (self.__class__.__name__, ("called" if self.has_called else "uncalled"), self.caller)
