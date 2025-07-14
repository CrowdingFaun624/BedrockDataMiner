from typing import TYPE_CHECKING, Any, Self, Sequence

import Utilities.Exceptions as Exceptions
from Component.Component import Component
from Component.Field.ComponentField import ComponentField, OptionalComponentField
from Component.Field.Field import Field
from Component.Pattern import Pattern
from Component.Structure.StructureComponent import StructureComponent
from Utilities.Trace import Trace
from Utilities.TypeUtilities import TypeSet

if TYPE_CHECKING:
    from Component.Structure.TypeAliasComponent import TypeAliasComponent

type VerifyComponentType = ComponentField[StructureComponent]|OptionalComponentField[StructureComponent]

TYPE_ALIAS_PATTERN:Pattern["TypeAliasComponent"] = Pattern("is_type_alias")

class AbstractTypeField(Field):

    __slots__ = (
        "_types",
        "contained_by_field",
        "default_fields",
        "is_resolved",
        "must_be_fail_message",
        "must_be_types",
        "subcomponent_data",
        "type_set",
        "types",
        "verify_with_component",
    )

    _types: Sequence["type|TypeAliasComponent"]

    def __init__(self, subcomponent_data:Any, path: tuple[str,...], cumulative_path:tuple[str,...]|None=None) -> None:
        '''
        :subcomponent_data: The name of the type or types.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        '''
        super().__init__(path, cumulative_path)
        self.subcomponent_data = subcomponent_data
        self.types:tuple[type,...] # used as cached value in `types` property.
        self.verify_with_component:VerifyComponentType|None=None
        self.must_be_types:TypeSet|None = None
        self.must_be_fail_message:str|None = None
        self.contained_by_field:AbstractTypeField|None = None
        self.default_fields:list[AbstractTypeField] = []
        self.is_resolved:bool = False
        self.type_set:set[type]|None = None

    def check(self, source_component:"Component", trace:Trace) -> None:
        with trace.enter_keys(self.trace_path, ...):
            super().check(source_component, trace)
            if self.verify_with_component is not None:
                subcomponent = self.verify_with_component.subcomponent
                component_types = self.types
                if subcomponent is None:
                    trace.exceptions(
                        Exceptions.ComponentTypeRequiresComponentError(source_component, value_type)
                        for value_type in component_types
                        if value_type in self.domain.type_stuff.requires_subcomponent_types
                    )
                else:
                    if set(component_types) != subcomponent.my_type:
                        trace.exception(Exceptions.ComponentMismatchedTypesError(source_component.trace_name, sorted(component_types, key=lambda type: type.__name__), subcomponent.trace_name, sorted(subcomponent.my_type, key=lambda type: type.__name__)))
            if self.must_be_types is not None:
                trace.exceptions(
                    Exceptions.ComponentTypeInvalidTypeError(type, self.must_be_types, message=self.must_be_fail_message)
                    for type in self.types
                    if type not in self.must_be_types
                )
            if self.contained_by_field is not None:
                trace.exceptions(
                    Exceptions.ComponentTypeContainmentError(supercomponent_type, component_type)
                    for component_type in self.types
                    for supercomponent_type in self.contained_by_field.types
                    if (containment_types := self.domain.type_stuff.containment_types.get(supercomponent_type)) is not None
                    if component_type not in containment_types
                )

    def resolve_link_finals(self, trace:Trace) -> None:
        with trace.enter_keys(self.trace_path, ...):
            self.resolve()

    def resolve(self) -> tuple[type,...]:
        if self.is_resolved: # since all Components call `resolve_link_finals` on all Fields and Fields call it on each other, it may be called twice.
            return self.types
        self.is_resolved = True
        types:set["type|TypeAliasComponent"] = set()
        output:list[type] = []
        if len(self._types) == 0 and len(self.default_fields) != 0:
            for default_field in self.default_fields:
                for subtype in default_field.resolve():
                    if subtype in types: continue
                    output.append(subtype)
                    types.add(subtype)
        else:
            for subcomponent in self._types:
                if subcomponent in types: continue
                if isinstance(subcomponent, type):
                    output.append(subcomponent)
                    types.add(subcomponent)
                else: # isinstance(TypeAliasComponent)
                    for subtype in subcomponent.final.resolve():
                        if subtype in types: continue
                        output.append(subtype)
                        types.add(subtype)
                    types.add(subcomponent)
        self.types = tuple(output)
        if self.type_set is not None:
            self.type_set.update(self.types)
        return self.types

    def add_to_set(self, _set:set[type]) -> Self:
        '''
        This Field will add to `_set` when its types are set.
        '''
        self.type_set = _set
        return self

    def verify_with(self, component_field:VerifyComponentType) -> Self:
        '''
        Makes this TypeField verify using this component field when `check` is called.
        :component_field: The ComponentField or OptionalComponentField to check with.
        '''
        self.verify_with_component = component_field
        return self

    def must_be(self, types:TypeSet, *, fail_message:str|None=None) -> Self:
        '''
        Makes this TypeField check that all of its types are a member of `types`.
        :types: The tuple of types that this TypeField must be.
        '''
        self.must_be_types = types
        self.must_be_fail_message = fail_message
        return self

    def contained_by(self, type_field:"AbstractTypeField") -> Self:
        '''
        Makes this TypeField check that its types are those that can be contained by the types in `type_field`.
        :type_field: The TypeField of types that contain this TypeField's types.
        '''
        self.contained_by_field = type_field
        return self

    def default_to(self, type_field:"AbstractTypeField") -> Self:
        '''
        If this TypeField is empty, returns the types of `type_field` instead.
        '''
        self.default_fields.append(type_field)
        return self

    def make_default(self, type_field:"AbstractTypeField") -> Self:
        '''
        Makes `type_field` return this TypeField's types by default.
        '''
        type_field.default_to(self)
        return self
