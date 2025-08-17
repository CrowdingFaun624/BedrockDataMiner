from types import EllipsisType
from typing import TYPE_CHECKING, ClassVar, Final, Iterable

from Component.Field.Errors import Errors
from Component.PropagatingVariables import PropagatingVariables
from Component.Scope import Scope
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Field.FieldFactory import FieldFactory

class Field[R]():
    """
    An object created by the parser that handles information about Components, Scripts, and other things.

    :param factory: The FieldFactory that created this Field.
    :param scope: The Scope that this Field was created with.
    :param error: The first step this Field cannot complete.
    """

    allow_abstract: ClassVar[bool] = False
    """
    If True, this Field may be abstract, preventing it from being evaluated unless referenced.
    """
    requires_variables: ClassVar[bool] = True
    """
    If False, Scopes used to reference this Field will drop their Variables, overriding Variables, and overriding Fields. Good for caching.
    """

    __slots__ = (
        "created_final",
        "end_column",
        "end_index",
        "end_line",
        "error",
        "factory",
        "finalized",
        "linked_final",
        "name",
        "scope",
        "start_column",
        "start_index",
        "start_line",
    )

    def __init__(self, factory:"FieldFactory", scope:Scope, error:Errors) -> None:
        self.error = error
        """
        The first step this Field cannot complete
        """
        self.factory: Final = factory
        self.start_index: Final = factory.reader_scope.start_index
        self.start_line: Final
        self.start_column: Final
        self.start_line, self.start_column = factory.group.reader.newlines[self.start_index]
        self.end_index: Final = factory.reader_scope.end_index
        self.end_line: Final
        self.end_column: Final
        self.end_line, self.end_column = factory.group.reader.newlines[self.end_index]
        self.created_final = False # used to not repeat the calculations of create_final
        self.linked_final = False # used to not repeat the calculations of link_final. Reassigned to True by each implementation of the method.
        self.finalized = False # used to not repeat the calculations of finalize
        self.scope: Final = scope
        self.name = self.factory.group.full_name + self.factory.name # get full name

    def narrow(self, error:Errors) -> "Errors":
        """
        Narrows `self.error` according to `error`. Returns the resulting Errors.
        """
        self.error = self.error.narrow(error)
        return self.error

    def narrows(self, errors:Iterable[Errors]) -> "Errors":
        """
        Narrows `self.error` according to many Errors. Returns the soonest value. Cannot be empty.
        """
        self.error = self.error.narrows(errors)
        return self.error

    def create_field(self, memo:set["FieldFactory"], trace:Trace) -> Errors:
        """
        The second step (after parsing). Secures references to other Fields.
        Thinking about what this Field will return is for `create_final`.

        :param memo: A memo that contains FieldFactories only in places that could loop, like Field references.
        """
        return self.error

    def create_final(self, trace:Trace) -> Errors:
        """
        The third step (after create_field). Evaluates Variables and prepares for linking.
        """
        self.created_final = True
        return self.error

    def get_final_type(self, trace:Trace) -> tuple[tuple[type,...], Errors]:
        """
        A method which may be called during or after `create_final`.
        """
        ...

    def link_final_early(self, trace:Trace) -> tuple[R|EllipsisType, PropagatingVariables|None|EllipsisType, Errors]:
        """
        Returns this Field's final value (and PropagatingVariables) without trying to fill it in all the way.
        Only necessary if this Field may reference itself.
        May return an Ellipsis even if there are no errors.
        """
        return ..., None, self.error

    def link_final(self, trace:Trace) -> tuple[R|EllipsisType, PropagatingVariables|None, Errors]:
        """
        The fourth step (after create_final). Links all Fields togethers.

        :returns: The final object of this Field (or ellipsis if there was an error) and a PropagatingVariables (or None).
        """
        ...

    def finalize(self, trace:Trace) -> Errors:
        """
        The fifth step (after link_final). Checks if Components are assembled correctly.
        """
        self.finalized = True
        return self.error

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"

    @property
    def optional_scope(self) -> Scope|None:
        """
        Returns the `scope` attribute if it exists, otherwise None.
        """
        return self.scope if hasattr(self, "scope") else None

    # __eq__ and __hash__ should be implemented assuming `create_field` has not been called.

    def __eq__(self, value: object) -> bool:
        raise NotImplementedError(self.__class__.__name__)

    def __hash__(self) -> int:
        raise NotImplementedError(self.__class__.__name__)
