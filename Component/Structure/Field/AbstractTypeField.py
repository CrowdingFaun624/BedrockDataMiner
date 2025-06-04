from typing import Any, Self

import Utilities.Exceptions as Exceptions
from Component.Component import Component
from Component.Field.ComponentField import ComponentField, OptionalComponentField
from Component.Field.Field import Field
from Component.Structure.StructureComponent import StructureComponent
from Utilities.Trace import Trace
from Utilities.TypeUtilities import TypeSet

type VerifyComponentType = ComponentField[StructureComponent]|OptionalComponentField[StructureComponent]

class AbstractTypeField(Field):

    __slots__ = (
        "contained_by_field",
        "default_fields",
        "final_types",
        "must_be_fail_message",
        "must_be_types",
        "subcomponent_data",
        "type_set",
        "verify_with_component",
    )

    _types: tuple[type,...]

    def __init__(self, subcomponent_data:Any, path: tuple[str,...]) -> None:
        super().__init__(path)
        self.subcomponent_data = subcomponent_data
        self.final_types:tuple[type,...]|None = None # used as cached value in `types` property.
        self.verify_with_component:VerifyComponentType|None=None
        self.must_be_types:TypeSet|None = None
        self.must_be_fail_message:str|None = None
        self.contained_by_field:AbstractTypeField|None = None
        self.default_fields:list[AbstractTypeField] = []
        self.type_set:set[type]|None = None

    @property
    def types(self) -> tuple[type,...]:
        if self.final_types is None:
            if len(self._types) == 0 and len(self.default_fields) != 0:
                output:list[type] = []
                inclusion:set[type] = set() # ordered result.
                for default_field in self.default_fields:
                    for subtype in default_field.types:
                        if subtype in inclusion: continue
                        output.append(subtype)
                        inclusion.add(subtype)
                self.final_types = tuple(output)
            else:
                self.final_types = self._types
        return self.final_types

    def check(self, source_component:"Component", trace:Trace) -> None:
        with trace.enter_keys(self.trace_path, self.subcomponent_data):
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
                        trace.exception(Exceptions.ComponentMismatchedTypesError(source_component, sorted(component_types, key=lambda type: type.__name__), subcomponent, sorted(subcomponent.my_type, key=lambda type: type.__name__)))
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
        '''
        Resolves all TypeAliases into types.
        Cannot be called before all TypeAliases are set.
        Cannot be called before `set_field`.
        '''
        with trace.enter_keys(self.trace_path, ...):
            super().resolve_link_finals(trace)

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
