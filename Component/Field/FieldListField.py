from typing import Callable, Iterator, MutableSequence, TypeVar

import Component.Field.Field as Field
import Component.Field.FieldContainer as FieldContainer

a = TypeVar("a", bound=Field.Field, covariant=True)

class FieldListField(FieldContainer.FieldContainer[a]):
    '''
    Field that contains other Fields.
    '''

    def __init__(self, fields:MutableSequence[a], path:list[str|int]) -> None:
        super().__init__(fields, path)

    def extend(self, new_fields:Iterator[a]) -> None:
        '''
        Adds new Fields to this Field.
        :new_fields: The sequence of Fields to add.
        '''
        self.fields.extend(new_fields)

    def extend_from_field_list(self, field_list:"FieldListField") -> None:
        '''
        Adds new Fields from the given FieldListField to this Field.
        :field_list: The FieldListField to take Fields from.
        '''
        self.fields.extend(field_list.fields)

    b = TypeVar("b")

    def for_each(self, function:Callable[[a],b]) -> None:
        '''
        Calls the given function on each Field in this Field.
        :function: The function to use.
        '''
        for field in self.fields:
            function(field)

    def map(self, function:Callable[[a],b]) -> Iterator[b]:
        '''
        Calls the given function on each Field in this Field, and returns the results in the same order.
        :function: The function to use.
        '''
        return map(function, self.fields)

    def __iter__(self) -> Iterator[a]:
        yield from self.fields

    def __len__(self) -> int:
        return len(self.fields)
