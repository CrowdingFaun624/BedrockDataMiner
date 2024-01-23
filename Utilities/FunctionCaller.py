from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T") # I love type hinting

class FunctionCaller(Generic[T]):
    def __init__(self, target:Callable[..., T], args:list[Any]=None, kwargs:dict[str,Any]=None) -> None:
        if not isinstance(target, Callable):
            raise TypeError("`target` is not a Callable!")
        if args is not None and not isinstance(args, list) and args is not None:
            raise TypeError("`args` is not a list or None!")
        if not isinstance(kwargs, dict) and kwargs is not None:
            raise TypeError("`kwargs` is not a dict or None!")
        if kwargs is not None and any(not isinstance(key, str) for key in kwargs):
            raise TypeError("`kwargs` has a key that is not a str!")
        
        self.target = target
        self.args = [] if args is None else args
        self.kwargs = {} if kwargs is None else kwargs
    
    def __call__(self) -> T:
        return self.target(*self.args, **self.kwargs)

class WaitValue(Generic[T]):
    '''Does not call the FunctionCaller until `get` is called. It then stores the output of the FunctionCaller for future calls of `get`.'''
    def __init__(self, caller:FunctionCaller[T]) -> None:
        if not isinstance(caller, FunctionCaller):
            raise TypeError("`caller` is not a FunctionCaller!")
        self.caller = caller
        self.has_called = False
        self.value = None
    def get(self) -> T:
        if not self.has_called:
            self.has_called = True
            self.value = self.caller()
        return self.value
