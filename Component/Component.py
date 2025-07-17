from types import EllipsisType
from typing import TYPE_CHECKING, Any, Mapping, Self, Sequence

import Component.Expression.Variable as Variable  # import loop
import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions
from Component.Expression.Expression import Expression
from Component.Permissions import (
    InheritancePermissions,
    InheritanceUsage,
    InlinePermissions,
    InlineUsage,
)
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Capabilities import Capabilities
    from Component.ComponentTyping import CreateComponentFunction
    from Component.Field.Field import Field
    from Component.Group import Group
    from Component.InheritedComponent import InheritedComponent
    from Component.ScriptImporter import ScriptSetSetSet
    from Utilities.TypeVerifier import TypedDictTypeVerifier

INVALID_NAME_CHARS = set(" \t\r\n\f\v!@#$%^&*()=[]{}\\|;'\",<>/?`") # most puncuation characters except "._:"
INVALID_NAME_CHARS_DISPLAY = list("!@#$%^&*()=[]{}\\|;'\",<>/?`")
INVALID_NAMES:set[str] = {"*", "type", "inherit", "self", "super", "default_type", "group_aliases", "^"}

INVALID_NAME_CHARS_FILE = set("<>:\"\\/|?*")
INVALID_NAMES_FILE:set[str] = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(0, 10)} | {f"LPT{i}" for i in range(0, 10)}

def is_number(name:str) -> bool: # way of expressing numbers in Expressions.
    if len(name) >= 2 and (name[0].isnumeric() or name[0] == "-"):
        if name[-1] == "i":
            try:
                int(name.removesuffix("i"))
                return True
            except ValueError:
                pass
        if name[-1] == "f":
            try:
                float(name.removesuffix("f"))
                return True
            except ValueError:
                pass
    return False

class Component[a]():

    class_name:str = "Component"
    my_capabilities:"Capabilities"
    type_verifier:"TypedDictTypeVerifier"
    script_referenceable:bool = False
    restrict_to_file_names:bool = False
    '''
    If the final of this Component may be accessed directly by Scripts.
    '''
    inline_permissions:InlinePermissions = InlinePermissions.mixed
    inheritance_permissions:InheritancePermissions = InheritancePermissions.mixed

    __slots__ = (
        "abstract",
        "completed_init",
        "data",
        "domain",
        "expressions",
        "evaluated_data",
        "fields",
        "final",
        "group",
        "index",
        "inherit_parent",
        "inline_components",
        "inline_parent",
        "is_reference_inheritance",
        "links_to_other_components",
        "name",
        "parents",
        "reference_inheritance_cache",
        "variable_bools",
        "variable_sets",
        "variables", # different thing from `variable_bools` and `variable_sets`
        "variables_display",
    )

    def __init__(
            self,
            data:dict[str,Any]|Any,
            name:str,
            domain:"Domain.Domain",
            group:"Group",
            index:int|None,
            trace:Trace,
            *,
            below_variables:Mapping[str,Any]|None=None,
            above_variables:Mapping[str,"Variable.Variable"]|None=None,
            inherit:bool=False,
            reference_inheritance:bool=False, # If True, Expressions contained by `above_variables` will be copied to set their source_component to self, removing all references from the original parent Component.
        ) -> None:
        self.data = data
        self.name = name
        self.domain = domain
        self.group = group
        self.index = index

        self.links_to_other_components:list[Component] = [] # contains Components linked to by Fields and also the Component this Component inherits from.
        self.parents:list[Component] = []
        self.final:a
        self.inline_components:list[Component]
        self.inline_parent:Component|None = None
        self.inherit_parent:Component|None = None # The Component that this one inherited from
        self.variable_bools, self.variable_sets = self.get_propagated_variables()
        self.is_reference_inheritance:bool = False
        self.reference_inheritance_cache:dict[int,Component] = {} # key is hash of Variables in sorted order, value is the resulting Component.
        self.variables_display:str = "" # overridden by copy_reference. Sole purpose is for __repr__. Without this, many different Components would look the same.
        # Must store all reference inheritance Components from this Component.

        self.completed_init:bool = False
        with trace.enter(self, self.name, ...):
            name_exception:bool = False
            if index is not None and any(char in INVALID_NAME_CHARS for char in name):
                trace.exception(Exceptions.ComponentInvalidNameCharacterError(self, INVALID_NAME_CHARS_DISPLAY, "and whitespace characters"))
                name_exception = True
            elif index is not None and name in INVALID_NAMES:
                trace.exception(Exceptions.ComponentInvalidNameError(self, sorted(INVALID_NAMES)))
                name_exception = True
            elif index is not None and self.restrict_to_file_names and any(char in INVALID_NAME_CHARS_FILE for char in name):
                trace.exception(Exceptions.ComponentInvalidNameCharacterError(self, list(INVALID_NAME_CHARS_FILE), "(must be a valid file name)"))
                name_exception = True
            elif index is not None and self.restrict_to_file_names and name.upper() in INVALID_NAMES_FILE:
                trace.exception(Exceptions.ComponentInvalidNameError(self, sorted(INVALID_NAMES_FILE), "(must be a valid file name; case insensitive)"))
                name_exception = True
            elif index is not None and is_number(name):
                trace.exception(Exceptions.ComponentNameNumberError(self))
                name_exception = True
            if name_exception:
                self.fields = ()
                return

            # items may be Variables
            self.expressions:list[Expression] = []
            self.variables:dict[str,Variable.Variable] = {}

            if below_variables is not None:
                # below_variables is not checked for unusedness since Components may declare Variables that aren't used in subComponents.
                unused_below_variables:set[str] = set(below_variables.keys())
                # reference_inheritance can never be True in here, but I'm putting it in just to be safe.
                self.variables.update((variable_name, Variable.Variable(variable_name).set_value(value.copy(self) if isinstance(value, Expression) else value)) for variable_name, value in below_variables.items())
            else: unused_below_variables = set()

            used_variables:set[str] = set()
            from Component.Expression.ExpressionParser import scan_for_expressions
            self.data:dict[str,Any]|Any = scan_for_expressions(data, self, self.variables, used_variables, reference_inheritance) # overwrite previous `self.data` with a copy with created/updated Expressions.

            for variable_key in [key for key in data if key.startswith("$")]: # list comprehension to avoid modifying data while iterating.
                with trace.enter_key(variable_key, self.data[variable_key]):
                    variable_name = variable_key.removeprefix("$")
                    if variable_name not in self.variables:
                        self.variables[variable_name] = Variable.Variable(variable_name)
                    self.variables[variable_name].set_value(self.data.pop(variable_key))
                    unused_below_variables.discard(variable_name)

            if above_variables is not None:
                unused_above_variables:set[str] = set(above_variables.keys())
                # an above Variable can be unused when a Component inherits from a Component that has Variables, but overwrites the places where they are used.
                for variable_name, value in above_variables.items():
                    with trace.enter_key(variable_name, value):
                        if variable_name not in self.variables:
                            self.variables[variable_name] = Variable.Variable(variable_name)
                        variable = value.copy(self)
                        if variable_name in self.variables and not self.variables[variable_name].undefined:
                            variable.set_value(self.variables[variable_name].value)
                        self.variables[variable_name] = variable
                        unused_below_variables.discard(variable_name)
                for variable_name, value in above_variables.items(): # doing this after because some Variables may still be undefined during.
                    with trace.enter_key(variable_name, value):
                        used_variables.update(value.get_variables_used(self.variables))
            else: unused_above_variables = set()

            unused_below_variables -= used_variables
            for unused_below_variable in unused_below_variables:
                del self.variables[unused_below_variable]
            unused_above_variables -= used_variables
            for unused_above_variable in unused_above_variables:
                del self.variables[unused_above_variable]
            if not inherit:
                unused_variables = self.variables.keys() - used_variables
                trace.exceptions(Exceptions.VariableUnusedError(self, variable_name, self.variables[variable_name].value, sorted(used_variables)) for variable_name in unused_variables)

            # "abstract" key is popped because we don't want Components that inherit this to also be abstract.
            self.abstract:bool = self.data.get("abstract", False) or any(variable.undefined for variable in self.variables.values())
            if not inherit: # the object resulting from this InheritedComponent should remember this.
                self.data.pop("abstract", False)
            self.completed_init = True

    def init(self, trace:Trace) -> bool: # returns if there was an exception
        if hasattr(self, "fields"):
            raise RuntimeError(f"Called `init` on {self} twice!")
        if self.abstract:
            trace.exception(Exceptions.AbstractComponentError(self, [variable.name for variable in self.variables.values() if variable.undefined]))
            return True
        self.evaluated_data = self.data if len(self.expressions) == 0 else Variable.evaluate_expressions(self.data, self.variables)
        if self.verify_arguments(self.evaluated_data, trace):
            return True
        self.fields:Sequence["Field"] = self.initialize_fields(self.evaluated_data)
        for field in self.fields:
            field.set_component(self)
        return False

    def copy_inherit(self, other:"Component", trace:Trace, parent_variables:Mapping[str,"Variable.Variable"]) -> "Component|EllipsisType":
        '''
        Copies this Component, overlaying the name, Domain, Group, and data from other onto the new one.
        '''
        new_data = self.data.copy() # only shallow copy because Components cannot modify their original data.
        # (Actually can't, since `data` is a deep copy of `original_data` and that's what's given to initialize_fields)
        new_data.update(other.data)
        new_variables = self.variables.copy()
        new_variables.update(other.variables)
        below_variables = {variable_name: variable.value for variable_name, variable in parent_variables.items() if not variable.undefined}
        output = type(self)(new_data, other.name, other.domain, other.group, other.index, trace, below_variables=below_variables, above_variables=new_variables)
        with trace.enter(output, output.name, ...):
            self.link_components((output,))
            output.inherit_parent = self
            if not output.abstract and output.init(trace):
                return ...
            return output
        return ...

    def copy_reference(self, other:"InheritedComponent", global_groups:Mapping[str,Mapping[str,"Group"]], functions:"ScriptSetSetSet", create_component_function:"CreateComponentFunction", trace:Trace) -> "Component|EllipsisType":
        '''
        Copies this Component, keeping the same name, Domain, Group, but with new Variables only.
        '''
        if len(other.data) > 0: # since other is InheritedComponent, "inherit" and other keys will be removed.
            trace.exception(Exceptions.ReferenceInheritanceDataError(other, self))
            return ...
        new_variables = self.variables.copy()
        new_variables.update(other.variables)
        variables_hash = hash(tuple(variable.get_hash(new_variables) for _, variable in sorted(other.variables.items(), key=lambda item: item[0])))
        if (cached_item := self.reference_inheritance_cache.get(variables_hash)) is not None:
            return cached_item
        new_data = self.data.copy()
        new_data.update(other.data)
        output = type(self)(new_data, self.name, self.domain, self.group, self.index, trace, above_variables=new_variables, reference_inheritance=True)
        with trace.enter(output, output.name, ...):
            self.reference_inheritance_cache[variables_hash] = output
            self.link_components((output,))
            output.inherit_parent = self
            output.is_reference_inheritance = True
            if len(other.variables) > 0:
                output.variables_display = f"{{{", ".join(f"{variable_name}={repr(variable.dereference(new_variables))}" for variable_name, variable in other.variables.items())}}}"
            if not output.abstract and output.init(trace):
                return ...
            output.set_component(global_groups, functions, create_component_function, trace)
            return output
        return ...

    def check_permissions(self, field:"Field", inline_usage:InlineUsage, inheritance_usage:InheritanceUsage, trace:Trace) -> None:
        if inline_usage is not InlineUsage.unknown:
            if self.inline_permissions is InlinePermissions.inline and inline_usage is not InlineUsage.inline:
                trace.exception(Exceptions.PermissionInlineError(self, field, (InlineUsage.inline,), inline_usage))
            if self.inline_permissions is InlinePermissions.reference and inline_usage is not InlineUsage.reference:
                trace.exception(Exceptions.PermissionInlineError(self, field, (InlineUsage.reference,), inline_usage))
            if self.inline_permissions is InlinePermissions.none:
                trace.exception(Exceptions.PermissionInlineError(self, field, (), inline_usage))
        if inheritance_usage is not InheritanceUsage.unknown:
            if self.inheritance_permissions is InheritancePermissions.normal and inheritance_usage is not InheritanceUsage.normal:
                trace.exception(Exceptions.PermissionInheritanceError(self, field, (InheritanceUsage.normal,), inheritance_usage))
            if self.inheritance_permissions is InheritancePermissions.regular_inheritance and not (inheritance_usage is InheritanceUsage.normal or inheritance_usage is InheritanceUsage.regular_inheritance):
                trace.exception(Exceptions.PermissionInheritanceError(self, field, (InheritanceUsage.normal, InheritanceUsage.regular_inheritance), inheritance_usage))
            if self.inheritance_permissions is InheritancePermissions.reference_inheritance and not (inheritance_usage is InheritanceUsage.normal or inheritance_usage is InheritanceUsage.reference_inheritance):
                trace.exception(Exceptions.PermissionInheritanceError(self, field, (InheritanceUsage.normal, InheritanceUsage.reference_inheritance), inheritance_usage))

    @property
    def assume_used(self) -> bool:
        '''
        If True, unused warnings will not be raised for this Component or its children.
        '''
        return False

    def initialize_fields(self, data:Any) -> Sequence["Field"]:
        return ()

    def get_index(self) -> int:
        "Returns the index of this Component in the Group. Raises an error if it doesn't have an index."
        if self.index is None:
            raise Exceptions.AttributeNoneError("index", self)
        return self.index

    def get_inline_parent(self) -> "Component":
        "Returns the parent of this Component if it is an inline Component. If it isn't, an error is raised."
        if self.inline_parent is None:
            raise Exceptions.AttributeNoneError("inline_parent", self)
        return self.inline_parent

    def get_inline_component_name(self, path:tuple[str,...]) -> str:
        output = self.name + "".join(f"({item})" for item in path)
        return output

    def get_all_descendants(self, memo:set["Component"], trace:Trace) -> list["Component"]:
        '''
        Returns a list of the Component, its childern, its grandchildren, and so on.
        :memo: The set of all Components already added to the list, ensuring no duplicates or infinite loops.
        '''
        with trace.enter(self, self.trace_name, ...):
            result:list[Component] = []
            if self not in memo:
                result.append(self)
                memo.add(self)
                for child in self.links_to_other_components:
                    result.extend(child.get_all_descendants(memo, trace))
            return result
        return []

    def link_components(self, components:Sequence["Component"]) -> None:
        self.links_to_other_components.extend(components)
        for component in components:
            component.parents.append(self)

    @classmethod
    def verify_arguments(cls, data:Mapping[str,Any], trace:Trace) -> bool:
        return cls.type_verifier.verify(data, trace)

    def inheritance(
        self,
        memo: set["Component"],
        global_groups:Mapping[str,Mapping[str,"Group"]],
        parent_variables:dict[str,Variable.Variable],
        functions:"ScriptSetSetSet",
        create_component_function:"CreateComponentFunction",
        trace: Trace,
    ) -> "Component|Self|EllipsisType":
        # overridden by InheritedComponent
        return self

    def set_component(
        self,
        global_groups:Mapping[str,Mapping[str,"Group"]],
        functions:"ScriptSetSetSet",
        create_component_function:"CreateComponentFunction",
        trace:Trace,
    ) -> None:
        '''Links this Component to other Components'''
        if self.abstract: return # Nothing to set if it's abstract.
        with trace.enter(self, self.trace_name, ...):
            self.inline_components = []
            for field in self.fields:
                linked_components, new_inline_components = field.set_field(self, self.group, global_groups, functions, create_component_function, trace)
                self.link_components(linked_components)
                self.inline_components.extend(new_inline_components)
            for inline_component in self.inline_components:
                inline_component.set_component(global_groups, functions, create_component_function, trace)
            # we don't iterate over reference_inheritance_cache here because the cache is still in the process of being built.
            # set_component is handled by copy_reference.

    def create_final_component(self, trace:Trace) -> a|EllipsisType:
        '''Creates this Component's final Structure or StructureBase, if applicable.'''
        with trace.enter(self, self.trace_name, ...):
            if not self.abstract:
                for inline_component in self.inline_components:
                    inline_component.final = inline_component.create_final_component(trace)
                output = self.create_final(trace)
            else: output = ...
            for reference_component in self.reference_inheritance_cache.values():
                reference_component.final = reference_component.create_final_component(trace)
            return output
        return ...

    def create_final(self, trace:Trace) -> a|EllipsisType:
        '''
        Method overridden by subclasses. Returns the Component's object.

        You do not have to wrap this method in `with trace.enter` or use super().create_final.
        '''
        ...

    def link_final_component(self, trace:Trace) -> None:
        '''Links this Component's final object to other final objects.'''
        with trace.enter(self, self.trace_name, ...):
            if not self.abstract:
                for field in self.fields:
                    field.resolve_link_finals(trace)
                for inline_component in self.inline_components:
                    inline_component.link_final_component(trace)
                self.link_finals(trace)
            for reference_component in self.reference_inheritance_cache.values():
                reference_component.link_final_component(trace)

    def link_finals(self, trace:Trace) -> None:
        '''
        Method overridden by subclasses. Links things from Fields to the final.

        You do not have to wrap this method in `with trace.enter` or use super().link_finals.
        '''
        pass

    def check_component(self, trace:Trace) -> None:
        '''Make sure that this Component's types are all in order; no error could occur.'''
        with trace.enter(self, self.trace_name, ...):
            if not self.abstract:
                for field in self.fields:
                    field.check(self, trace)
                for inline_component in self.inline_components:
                    inline_component.check_component(trace)
                self.check(trace)
            for reference_component in self.reference_inheritance_cache.values():
                reference_component.check_component(trace)

    def check(self, trace:Trace) -> None:
        '''
        Method overridden by subclasses. Raises exceptions.

        You do not have to wrap this method in `with trace.enter` or use super().check.
        '''
        pass

    def finalize_component(self, trace:Trace) -> None:
        '''Used to call on the structure once all Structures and Components are guaranteed to be linked.'''
        with trace.enter(self, self.trace_name, ...):
            if not self.abstract:
                for field in self.fields:
                    field.finalize(trace)
                for inline_component in self.inline_components:
                    inline_component.finalize_component(trace)
                self.finalize(trace)
            for reference_component in self.reference_inheritance_cache.values():
                reference_component.finalize_component(trace)

    def finalize(self, trace:Trace) -> None:
        '''
        Method overridden by subclasses. Called once all Structures and Components are guaranteed to be linked.

        You do not have to wrap this method in `with trace.enter` or use super().finalize.
        '''
        pass

    def get_propagated_variables(self) -> tuple[dict[str,bool], dict[str,set]]:
        return {}, {}

    def propagate_variables(self, trace:Trace) -> bool:
        if self.abstract: return False
        with trace.enter(self, self.trace_name, ...):
            has_changed = False
            # bools
            for variable_name, variable_value in self.variable_bools.items():
                with trace.enter_key(variable_name, variable_value):
                    for child in self.links_to_other_components:
                        other_value = child.variable_bools.get(variable_name)
                        if other_value is None:
                            continue
                        if other_value and not variable_value:
                            self.variable_bools[variable_name] = other_value
                            has_changed = True
            # sets
            for variable_name, variable_value in self.variable_sets.items():
                with trace.enter_key(variable_name, variable_value):
                    for child in self.links_to_other_components:
                        other_value = child.variable_sets.get(variable_name)
                        if other_value is None:
                            continue
                        length_before = len(variable_value)
                        variable_value.update(other_value)
                        has_changed = has_changed or len(variable_value) != length_before
            return has_changed
        return False

    def __hash__(self) -> int:
        return hash((self.name, self.group, self.domain))

    @property
    def full_name(self) -> str:
        return f"{self.domain.name}!{self.group.name}/{self.name}{self.variables_display}"

    @property
    def trace_name(self) -> str:
        '''
        String to keep Traces terse but giving distinguishing information.
        '''
        return f"{self.name}{self.variables_display}"

    def __repr__(self) -> str:
        return f"<{self.class_name} {self.domain.name}!{self.group.name}/{self.name}{self.variables_display}>"
