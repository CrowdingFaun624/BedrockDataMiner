from types import EllipsisType
from typing import TYPE_CHECKING, Any, Callable, Final, Self, Sequence

from Component.Field.Errors import Errors
from Component.Field.Variable import Variable
from Component.Reader import Reader
from Component.Scope import Scope
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Field.Field import Field
    from Component.Group import Group


class FieldFactory[F: "Field"]():
    """
    Creates Fields using a Scope.

    :param reader: The Reader that created this FieldFactory.
    :param abstract: If this FieldFactory is abstract, preventing steps from being applied to it unless it is referenced.
    :param error: The first step the Field or this FieldFactory cannot complete.
    :param field_function: A function that takes this FieldFactory and a Scope and returns a Field.
    """

    __slots__ = (
        "abstract",
        "error",
        "field_function",
        "field_type",
        "fields",
        "full_name",
        "group",
        "index",
        "is_inline",
        "key",
        "name",
        "reader_scope",
        "subfields",
    )

    def __init__(
        self,
        reader:Reader,
        abstract:bool,
        error:Errors,
        subfields:Sequence[tuple[str,"FieldFactory"]],
        field_type:type[F],
        field_function:Callable[[Self, Scope],F],
    ) -> None:
        self.field_function = field_function
        self.reader_scope = reader.current_scope()
        self.abstract = abstract
        self.error = error
        self.subfields = subfields
        self.field_type = field_type
        self.name = str(id(self)) # intermediate name so __repr__ still works
        self.full_name = str(id(self))
        self.key:str

    def narrow(self, error:Errors) -> Errors:
        """
        Narrows `self.error` according to `error`. Returns the resulting Errors.
        """
        self.error = self.error.narrow(error)
        return self.error

    def set_field(self, group:"Group", name:str, key:str, index:int, trace:Trace, is_inline:bool=True) -> Errors:
        """
        Gives various information to this FieldCreator after parsing is done.

        :param group: The Group this FieldFactory originates from.
        :param name: The name of this FieldFactory, found by its position within the Group.
        :param key: The key that this Field is in.
        :param index: The index of this FieldFactory (or its root parent) within its Group.
        :param is_inline: Set to False by Importer. Describes if the FieldFactory is referenceable from the root level.
        """
        # acts even on abstract Fields.
        self.group = group
        self.name = name
        self.full_name = f"{group.domain.name}!{group.name}{self.name}"
        self.key = key
        self.index = index
        self.is_inline = is_inline
        self.fields:dict[Scope, F] = {}
        if self.abstract and not self.field_type.allow_abstract:
            trace.exception(RuntimeError(f"{self.field_type.__name__} cannot be abstract"))
            self.narrow(Errors.create_field)
        for key, subfield in self.subfields:
            self.narrow(subfield.set_field(group, name + (f"(${key})" if issubclass(subfield.field_type, Variable) else f"({key})"), key, index, trace))
        return self.error

    def create_field_shallow(self, scope:Scope, trace:Trace) -> F|EllipsisType:
        """
        Returns a Field associated with a Scope for this FieldFactory.
        If one was already created with this Scope, it returns that one.
        Does not call `create_field` on the result. Intended for use by Importer only.
        """
        # don't bother to hash the Scope or do without_variables
        output = self.fields[scope] = self.field_function(self, scope)
        return output

    def create_field(self, scope:Scope, memo:set["FieldFactory"], trace:Trace) -> tuple[F|EllipsisType, Errors]:
        """
        Returns a Field associated with a Scope for this FieldFactory.
        If one was already created with this Scope, it returns that one.
        """
        if not self.field_type.requires_variables:
            scope = Scope.new_empty()
        if (already_field := self.fields.get(scope)) is not None:
            return already_field, already_field.error
        if self in memo:
            trace.exception(RuntimeError(f"Reference cycle involving {memo}"))
            return ..., Errors.create_field
        output = self.fields[scope] = self.field_function(self, scope)
        output.create_field(memo, trace)
        return output, output.error

    def create_final(self, scope:Scope, trace:Trace) -> Errors:
        """
        Creates the final value of the Field with the associated Scope. Intended to be used by Importer with an empty Scope.
        """
        return self.fields[scope].create_final(trace)

    def link_final(self, scope:Scope, trace:Trace) -> tuple[Any, Errors]:
        """
        Returns the final value of the Field with the associated Scope.
        """
        output, propagating_variables, error = self.fields[scope].link_final(trace)
        return output, error

    def finalize(self, scope:Scope, trace:Trace) -> Errors:
        """
        Finalizes the Field with the associated Scope.
        """
        return self.fields[scope].finalize(trace)

    def destroy(self) -> None:
        """
        Removes all potentially problematic attributes of this FieldFactory.
        """
        for scope, field in self.fields.items():
            scope.destroy()
            field.destroy()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.field_type.__name__} {self.full_name}>"

class FieldSlot[F:"Field"="Field"]():
    """
    An object unique to a single Field. It stores a Field in itself when
    `create_field` is called. It is used for ContainerField.
    """

    __slots__ = (
        "destroyed",
        "error",
        "field",
        "field_factory",
    )

    def __init__(self, field_factory:FieldFactory[F]) -> None:
        self.error = Errors.fine
        self.field_factory:Final[FieldFactory[F]] = field_factory
        self.field:F
        self.destroyed:bool = False

    def create_field(self, scope:Scope, trace:Trace) -> tuple["F|EllipsisType", Errors]:
        """
        Creates a new Field from the FieldFactory and stores it in the `field` attribute.
        Uses the FieldFactory's cache and calls `create_field` on the output.
        """
        # this method has no caching, but since it is only ever called by ContainerField,
        # the caching that the ContainerField has from its FieldFactory suffices.
        output, new_error = self.field_factory.create_field(scope, set(), trace)
        self.error = self.error.narrow(new_error)
        if output is not ...:
            self.field = output
        return output, self.error

    def destroy(self) -> None:
        if self.destroyed: return
        self.destroyed = True
        self.field_factory.destroy()
        del self.field_factory # type: ignore DESTROY
        if hasattr(self, "field"):
            self.field.destroy()
            del self.field

    def __repr__(self) -> str:
        if hasattr(self, "field"): # this allows for __repr__ to always function correctly.
            if hasattr(self.field, "name"):
                return f"<{self.__class__.__name__} {self.field}>"
            else:
                return f"<{self.__class__.__name__} {self.field.__class__.__name__}>"
        else:
            return f"<{self.__class__.__name__} {self.field_factory}>"

    def __eq__(self, value: object) -> bool:
        return isinstance(value, FieldSlot) and self.field_factory == value.field_factory

    def __hash__(self) -> int:
        return hash((FieldSlot, self.field_factory))
