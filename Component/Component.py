from typing import AbstractSet, Any, Mapping

from Component.ComponentObject import ComponentObject
from Component.Field.Field import Field
from Component.Group import Group
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictTypeVerifier

# for comparison, the old Component was about 500 lines long

class Component[R: ComponentObject, P:Mapping[Any, Any] = Mapping[Any, Any]]():
    """
    An object that creates and manages objects created by Components.
    When creating a new Component type, the following must be implemented:
    - `type_name`
    - `object_type`
    - `abstract`
    - `link_final`

    :param name: The name of this Component and the object it creates.
    :param field: The Field that created this Component.
    :param group: The Group that the Field was evaluated in.
    :param index: The index of this Field (or its root parent) in its Group.
    :param is_inline: If True, this Component's Field is contained by another Field.
    """

    type_name: str
    """
    The key used to refer to this Component type in cmp files.
    Required for all Component types, including abstract ones.
    """
    object_type: type[ComponentObject]
    abstract:bool
    """
    If True, this Component cannot be created directly but its object type can
    still be referenced.
    """

    type_verifier:TypedDictTypeVerifier = TypedDictTypeVerifier()

    __slots__ = (
        "fields",
        "final",
        "full_name",
        "group",
        "index",
        "is_inline",
        "name",
        "propagating_booleans",
        "propagating_sets",
    )

    def __init__(self, name:str, field:Field, group:Group, index:int, is_inline:bool) -> None:
        self.name = name
        self.group = group
        self.index = index
        self.is_inline = is_inline
        """
        The index of this Component's Field within its original Group.
        """
        self.full_name = self.group.full_name + self.name

        self.final:R
        """
        The result object of this Component. Of type `object_type`.
        """
        self.propagating_booleans: dict[str,bool]
        """
        Propagating booleans are sent upwards through Fields and Field references.
        The contents may be switched to True during `link_final`.
        """
        self.propagating_sets: dict[str,set[object]]
        """
        Propagating sets are sent upwards through Fields and Field references.
        The contents may be updated during `link_final`.
        """

    def __repr__(self) -> str:
        return f"<{self.type_name} {self.full_name}>"

    def create_final(self) -> None:
        """
        Initializes the object. Fields are not available at this point.
        may not be overridden by subclasses.
        """
        self.final = self.object_type( # type: ignore pretend that it is R (can't because it behaves weirdly with abstract)
            name=self.name,
            full_name=self.full_name,
            domain=self.group.domain,
            is_inline=self.is_inline,
        )

    def get_propagating_variables(self) -> tuple[dict[str,bool], dict[str,set[object]]]:
        """
        May be overridden by subclasses. Returns propagating booleans and propagating sets to propagate upwards through Fields and Field references.
        The resulting objects are stored in `self.propagating_booleans` and `self.propagating_sets`, respectively. These attributes may be modified
        during the `link_final` step. In `finalize`, the propagating variables from below will be passed as arguments.
        """
        return {}, {}

    def check(self, fields:P, trace:Trace) -> bool:
        """
        Creates any exceptions about this Component's Fields. Runs immediately before `link_final`.

        :param fields: A dictionary of the Field name to its final object.
        :returns: If there are any exceptions.
        """
        return self.type_verifier.verify(fields, trace)

    def link_final(self, fields:P) -> None:
        """
        Gives Field information to the object. May be overridden by subclasses.

        :param fields: A dictionary of the Field name to its final object.
        """
        self.fields = fields

    def post_check(self, fields:P, trace:Trace) -> bool:
        """
        Creates any exceptions about this Component's Fields.
        Runs after all Fields complete `link_final`.

        :param fields: A dictionary of the Field name to its final object.
        :returns: If there are any exceptions.
        """
        # we check it again because the data may have changed, e.g. keys being added to dictionaries.
        return self.type_verifier.verify(fields, trace)

    def finalize(self, propagating_booleans:Mapping[str,bool], propagating_sets:Mapping[str,AbstractSet[Any]], trace:Trace) -> bool:
        """
        Runs after all Fields complete `link_final`.

        :param propagating_booleans: Propagating booleans from this Component or its sub-Fields.
        :param propagating_sets: Propagating sets from this Component or its sub-Fields.
        :returns: If there are any exceptions.
        """
        return False
