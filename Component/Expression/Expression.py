from typing import TYPE_CHECKING, Any, Callable, Iterable, Self

from Utilities.Exceptions import InvalidStateError, ReaderSourceEndError

if TYPE_CHECKING:
    from Component.Component import Component
    from Component.Expression.Variable import Variable

class Reader():

    __slots__ = (
        "index",
        "source",
    )

    def __init__(self, source:str) -> None:
        self.source:str = source
        self.index:int = 0

    def read(self, amount:int, back:int=0) -> str:
        if self.index + amount > len(self.source):
            raise ReaderSourceEndError(self, "because the end of the source was reached!")
        output = self.source[self.index:self.index+amount]
        self.index += amount - back
        return output

    def set(self, index:int) -> None:
        self.index = index

    def move(self, amount:int) -> None:
        self.index += amount

    def at_last(self) -> bool:
        return self.index >= len(self.source)

    def read_while(self, while_function:Callable[[str],bool]) -> str:
        '''
        Returns all characters from the current position while `while_function` returns True
        or the end of the source is reached.
        :while_function: A function that takes a single character.
        '''
        start = self.index
        for index in range(start, len(self.source)):
            if not while_function(self.source[index]):
                self.index = index
                return self.source[start:index]
        self.index = len(self.source)
        return self.source[start:]

    def move_while(self, while_function:Callable[[str],bool]) -> None:
        '''
        Moves forward while `while_function` returns True or the end of the source is reached.
        :while_function: A function that takes a single character.
        '''
        start = self.index
        for index in range(start, len(self.source)):
            if not while_function(self.source[index]):
                self.index = index
                return
        self.index = len(self.source) - 1
        return

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.index}/{len(self.source)} \"{self.source}\">"

class Expression():

    __slots__ = (
        "current_component",
        "source",
        "source_component",
        "variables_used",
    )

    def __init__(self, source_component:"Component", source:str|None=None) -> None:
        self.source_component = source_component
        self.variables_used:list[str] = []
        self.current_component = source_component
        self.source:str|None = source
        '''
        the string used to make this Expression only, not surrounding Expressions.
        '''

    def copy(self, new_component:"Component") -> "Expression":
        '''
        The base copy function. This method should call `self.copy_attrs`.
        :new_component: The Component to set the new Expression's `current_component` attribute to.
        '''
        output = type(self)(self.source_component)
        self.copy_attrs(output, new_component)
        return output

    def copy_attrs(self, new_expression:"Expression", new_component:"Component") -> None:
        '''
        A method for superclasses to call to make sure all attributes are correctly copied.
        '''
        new_expression.variables_used = self.variables_used
        new_expression.current_component = new_component
        new_expression.source = self.source

    def get_variables_used(self) -> Iterable[str]:
        '''
        Returns the Variable names used by this Expression and its sub-Expressions.
        '''
        return self.variables_used

    def evaluate(self, variables:dict[str,"Variable"]) -> Any:
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.source}>" if self.source is not None else f"<{self.__class__.__name__} id {id(self)}>"

    def __hash__(self) -> int:
        if self.source is None:
            raise InvalidStateError("Expression must have source defined to hash!")
        return hash((self.__class__, self.source))

    @classmethod
    def applicable(cls, reader:Reader, is_key:bool) -> bool:
        '''
        Returns if this Expression type can be used to parse `source`.
        This method should be fast. If it returns True, then an exception may be raised
        from `parse` to indicate this Expression is inapplicable. This method does not
        need to worry about the Reader's index.
        '''
        return True

    @classmethod
    def parse(cls, reader:Reader, source_component:"Component", is_key:bool) -> Self:
        ...
