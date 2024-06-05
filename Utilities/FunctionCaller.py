from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T") # I love type hinting

class FunctionCaller(Generic[T]):

    def __init__(self, target:Callable[..., T], args:list[Any]|None=None, kwargs:dict[str,Any]|None=None) -> None:
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
