import enum
from types import EllipsisType
from typing import TYPE_CHECKING, Any, Mapping

import Component.Field.Field as Field
from Component.Component import Component
from Component.Expression.Variable import Variable
from Component.Pattern import ALL_PATTERN
from Utilities.Exceptions import ComponentTypeInheritError, InheritanceLoopError
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    EnumTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)

if TYPE_CHECKING:
    from Component.ComponentTyping import CreateComponentFunction
    from Component.Group import Group
    from Component.ScriptImporter import ScriptSetSet
    from Domain.Domain import Domain

class InheritanceType(enum.Enum):
    inherit = "inherit"
    reference = "reference"

class InheritedComponent(Component):
    '''
    Any Component with the "inherit" key.
    '''

    class_name = "InheritedComponent"
    __slots__ = (
        "inheritance_type",
        "inherited",
        "result",
        "supercomponent",
    )

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("inherit", True, str),
        TypedDictKeyTypeVerifier("inheritance_type", False, EnumTypeVerifier({item.value for item in InheritanceType})),
        loose=True,
    )

    def __init__(self, data:dict[str,Any]|Any, name:str, domain:"Domain", group:"Group", index:int|None, trace:Trace) -> None:
        super().__init__(data, name, domain, group, index, trace, inherit=True)
        if "type" in data: # must be placed after super().__init__ or ComponentTypeInheritError cannot refer to `component.data`.
            trace.exception(ComponentTypeInheritError(self))
            return

        self.verify_arguments(self.data, trace) # checking for "inherit" type
        self.supercomponent = self.data.pop("inherit")
        self.inheritance_type = InheritanceType[self.data.pop("inheritance_type", "inherit")]
        self.result:Component|None = None # what is returned by `inheritance`. May be already set at `inheritance` due to inheritance chains.

    def init(self, trace: Trace) -> None:
        # super().init verifies arguments and initializes fields. Neither are desirable here.
        pass

    def inheritance(
        self,
        memo: set[Component],
        global_groups:Mapping[str,Mapping[str,"Group"]],
        parent_variables:dict[str,Variable],
        functions:"ScriptSetSet",
        create_component_function:"CreateComponentFunction",
        trace: Trace,
    ) -> Component|EllipsisType:
        # This method is not fully memoized. Inline Components cannot realistically do it because of the context from the parent.
        supercomponent = None
        with trace.enter(self, self.trace_name, ...):
            if self in memo:
                trace.exception(InheritanceLoopError(memo))
                return ...
            memo.add(self)
            if self.result is not None:
                return self.result
            supercomponent_that_may_be_an_ellipsis, _, _ = Field.choose_component(self.supercomponent, self, ALL_PATTERN, self.group, global_groups, trace, (), functions, create_component_function, None, allow_inherited=True)
            if supercomponent_that_may_be_an_ellipsis is ...: # exception occured.
                return ...
            supercomponent = supercomponent_that_may_be_an_ellipsis
            if isinstance(supercomponent, InheritedComponent):
                supercomponent_that_may_be_an_ellipsis = supercomponent.inheritance(memo, global_groups, parent_variables, functions, create_component_function, trace)
            if supercomponent_that_may_be_an_ellipsis is ...:
                return ...
            supercomponent = supercomponent_that_may_be_an_ellipsis
        # the following code is removed from the above Trace to clean up error messages.
        if supercomponent is None:
            return ...
        if self.inheritance_type is InheritanceType.inherit:
            output = supercomponent.copy_inherit(self, trace, parent_variables)
        else:
            output = supercomponent.copy_reference(self, global_groups, functions, create_component_function, trace)
        # After this, the new, non-Inherited Component will check for its abstractness, verify its arguments, and initialize its fields like normal.
        if output is not ...:
            self.result = output
        return output
