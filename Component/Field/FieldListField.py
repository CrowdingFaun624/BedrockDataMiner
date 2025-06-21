from typing import Callable, Iterator

from Component.Field.Field import Field
from Component.Field.FieldContainer import FieldContainer


class FieldListField[a: Field](FieldContainer[a]):
    '''
    Field that contains other Fields.
    '''

    __slots__ = ()

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

    def for_each[b](self, function:Callable[[a],b]) -> None:
        '''
        Calls the given function on each Field in this Field.
        :function: The function to use.
        '''
        for field in self.fields:
            function(field)

    def map[b](self, function:Callable[[a],b]) -> Iterator[b]:
        '''
        Calls the given function on each Field in this Field, and returns the results in the same order.
        :function: The function to use.
        '''
        return map(function, self.fields)

    def __iter__(self) -> Iterator[a]:
        yield from self.fields

    def __len__(self) -> int:
        return len(self.fields)
