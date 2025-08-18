from typing import TYPE_CHECKING, Final, Mapping

from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Field.Field import Field
    from Component.Field.Variable import Variable


class Scope():
    """
    Immutable object that handles the passing and overlaying of Variables and Fields.

    :param variables: Variables from above Fields.
    :param override_variables: Variables to place on top of `variables` and the Variables of the next Field.
    :param override_fields: Fields to place on top of the sub-Fields of the next Field.
    """

    __slots__ = (
        "_sub",
        "_without_variables",
        "hash",
        "override_fields",
        "override_variables",
        "variable_declarations",
        "variable_definitions",
    )

    def __init__(
        self,
        variable_declarations:Mapping[str,"Variable"],
        variable_definitions:Mapping[str,"Variable"],
        override_variables:Mapping[str,"Variable"]={},
        override_fields:Mapping[str,"Field"]={}
    ) -> None:
        self.variable_declarations:Final = variable_declarations
        self.variable_definitions:Final = variable_definitions
        self.override_variables:Final = override_variables # top of the sandwich is first
        self.override_fields:Final = override_fields
        self.hash:Final = hash((
            frozenset(tuple(self.variable_declarations.items())),
            frozenset(tuple(self.variable_definitions.items())),
            frozenset(tuple(self.override_variables.items())),
            frozenset(tuple(self.override_fields.items())),
        ))
        self._sub:Scope|None = None
        self._without_variables:Scope|None = None

    @classmethod
    def new_empty(cls) -> "Scope":
        """
        Returns an empty Scope.
        """
        return EMPTY_SCOPE

    def __hash__(self) -> int:
        return self.hash

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Scope) and self.hash == value.hash

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {len(self.variable_declarations)}, {len(self.variable_definitions)}, {len(self.override_variables)}, {len(self.override_fields)}>"

    def assert_no_overriding(self, trace:Trace) -> None:
        """
        Creates an Exception using `trace.exception` if `override_variables` or `override_fields` exist and are not empty.
        """
        if self.override_fields is not None and len(self.override_fields) > 0:
            trace.exception(RuntimeError("Overriding Fields are not allowed in this context"))
        if self.override_variables is not None and len(self.override_variables) > 0:
            trace.exception(RuntimeError("Overriding Variables are not allowed in this context"))

    @property
    def local_variables(self) -> Mapping[str,"Variable"]:
        """
        Combines Variables and stuff.
        Only Variables which were declared at or above this Field are available.
        """
        if len(self.override_variables) > 0:
            raise RuntimeError("Hey you're supposed to call `sub` on a Scope before `local_variables`.")
        output:dict[str,"Variable"] = {}
        for variable_name, declared_variable in self.variable_declarations.items():
            if (defined_variable := self.variable_definitions.get(variable_name)) is not None:
                declared_variable.assign_value(defined_variable)
                output[variable_name] = declared_variable
            else:
                # add the Variable even though it's undefined so that VariableReferenceField
                # can check it and produce a better error message.
                output[variable_name] = declared_variable
        return output

    @property
    def local_fields(self) -> Mapping[str,"Field"]:
        """
        The overriding Fields, if they exist.
        """
        return self.override_fields

    def sub(self) -> "Scope":
        """
        :returns: A VariableEnvironment suited for use on sub-Fields.
        """
        if self._sub is None:
            if len(self.override_variables) == 0 and len(self.override_fields) == 0:
                self._sub = self
            else:
                # Why this works: Only setting the value from above will be able to
                # work, since any defined Variable resets the stored declared Variable.
                # Because the declared Variable is specific to each Scope, assigning it
                # a value will not screw anything else over.
                new_variable_declarations:dict[str,"Variable"] = {}
                new_variable_declarations.update(self.variable_declarations)
                new_variable_definitions:dict[str,"Variable"] = {}
                new_variable_definitions.update(self.variable_definitions)
                for variable_name, variable in self.override_variables.items():
                    if variable.is_defined:
                        new_variable_definitions.pop(variable_name, None) # defining a Variable beneath its declaration creates a separate Variable.
                        new_variable_definitions[variable_name] = variable
                    if variable.is_declaration: # must go after variable.is_defined block
                        new_variable_declarations[variable_name] = variable
                self._sub = Scope(new_variable_declarations, new_variable_definitions)
        return self._sub

    def override(
        self,
        override_variables:Mapping[str,"Variable"],
        override_fields:Mapping[str,"Field"],
        *,
        forget_above_variables:bool=False,
    ) -> "Scope":
        """
        Overrides sub-Fields to use different Variables and Fields.

        :param override_variables: Variables to place on top of Variables of the sub-Field.
        :param override_fields: Fields to place on top of the Fields of the sub-Field.
        :param forget_above_variables: If True, Variables from above are forgotten.
        :returns: A new VariableEnvironment with the propeties described.
        """
        new_variables:dict[str,"Variable"] = {}
        new_variables.update(override_variables)
        # doing self.override_variables second to prioritize the old ones more.
        for old_variable_name, old_variable in self.override_variables.items():
            if old_variable.is_defined and (new_variable := new_variables.get(old_variable_name)) is not None and new_variable.is_declaration:
                # if there is a Variable declaration here and a definition from above, assign the definition to this declaration.
                new_variable.assign_value(old_variable.referenced_field)
            else:
                new_variables[old_variable_name] = old_variable
        new_fields:dict[str,"Field"] = {}
        new_fields.update(override_fields)
        new_fields.update(self.override_fields) # simply override everything
        output = Scope(
            variable_declarations={} if forget_above_variables else self.variable_declarations,
            variable_definitions={} if forget_above_variables else self.variable_definitions,
            override_variables=new_variables,
            override_fields=new_fields,
        )
        return output

EMPTY_SCOPE = Scope({}, {})
