from types import EllipsisType
from typing import (Any, Callable, Container, Hashable, Iterable, Mapping,
                    Protocol, Self, TypeIs, cast)

import Utilities.Exceptions as Exceptions

# TypeVerifier 2.0

__all__ = [
    "Dict",
    "EnumDatum",
    "Iter",
    "Key",
    "Simple",
    "TypeDatum",
    "TypedDatum",
    "UnionDatum",
]

class SupportsBool(Protocol):

    def __bool__(self) -> bool: ...

type LineType = tuple[int, str] # (indentation, line string)

class Trace():
    '''
    Object storing the relationship of a TypeDatum relative to the base
    TypeDatum.

    To use this Trace in an error message, call the `relationship` method with
    the `additional_trace` argument given in `observe`. The resulting string
    starts with a lowercase letter, and the user is free to call str.capitalize
    on it.

    For an error relating to a TypeDatum itself, supply the error with the
    TypeDatum; it has an internal representation.
    '''

    __slots__ = (
        "_relationship",
        "_representation",
    )

    def __init__(self, representation:list[str], relationship:list[str]|None=None) -> None:
        '''
        :representation: The starting representation to start this Trace with.
        :relationship: The starting relationship to start this Trace with.\
            Should only be non-None for the `copy` method.
        '''
        self._representation:list[str] = []
        '''
        A list of strings representing the position of a TypeDatum in its tree.
        '''
        self._relationship:list[str] = [] if relationship is None else relationship

    def copy(self, new_representation:str|None, new_relationship:str|None=None) -> "Trace":
        '''
        Copies the Trace with a new representation and relationship appended.

        :new_representation: A short string representing the path through the\
            parent TypeDatum to the child TypeDatum.
        :new_relationship: The relationship of the child TypeDatum with\
            regards to its parent, in the form of a string such as "data of ".
        '''
        representation_copy = self._representation.copy()
        if new_representation is not None:
            representation_copy.append(new_representation)
        relationship_copy = self._relationship.copy()
        if new_relationship is not None:
            relationship_copy.append(new_relationship)
        return Trace(representation_copy, relationship_copy)

    @property
    def representation(self) -> str:
        '''
        The string representing the TypeDatum's position within it.
        '''
        return "→".join(self._representation)

    def relationship(self, additional_trace:str, additional_data:str="") -> str:
        '''
        The relationship of this Trace related to the base of the TypeData
        tree.

        :additional_trace: The `additional_trace` parameter of\
            `TypeDatum.observe`.
        :additional_data: A string placed in front of the trace string. Should\
            take the form of "data of ".
        '''
        return f"{additional_data}{"".join(reversed(self._relationship))}{additional_data}data"

class TypeDatum[C, D, TD]():
    '''
    Abstract class that makes sure that arguments to anything meet the required
    specifications. When finished constructing this object, the `finalize`
    method should be called on it.
    '''

    __slots__ = (
        "_trace",
        "children",
        "has_transform_function",
    )

    allows_children_transform:bool = True
    '''
    If False, direct children of instances of this TypeDatum type cannot have
    any transform methods.
    '''

    def __init__(self, *children:tuple["TypeDatum", str|None, str|None]) -> None:
        '''
        :children: The direct descendent TypeData of this TypeDatum, the\
            path item of the child with respect to this object, and the\
            children's relationship to this object in the form of a string\
            such as "data of ".
        '''
        self.children:tuple[tuple[TypeDatum, str|None, str|None],...] = children
        self._trace:Trace|None = None

    @property
    def trace(self) -> Trace:
        if self._trace is None:
            raise Exceptions.AttributeNoneError("trace", self)
        return self._trace

    def __repr__(self) -> str:
        if self._trace is None:
            return f"<{self.__class__.__name__} unfinalized>"
        else:
            return f"<{self.__class__.__name__} {self._trace.representation}>"

    def observe(
        self,
        data:D,
        transform_context:C,
        additional_trace:str,
    ) -> tuple[TD|EllipsisType, list[LineType]]:
        '''
        Verifies that the data are correct, transforming it with the help of
        `transform_context. If errors are present, the output data must be an
        Ellipsis object (...)

        :data: The data this TypeDatum is verifying.
        :transform_context: The second parameter to all `transform` functions\
            in this TypeData tree.
        :additional_trace: Additional data to add to error messages. This\
            string should take the form of "data of ".
        '''
        # implemented by child classes.
        ...

    def finalize(self, name:str, trace:Trace|None=None) -> Self:
        '''
        :name: The name of this TypeData tree; used in the messages of errors\
            relating to the TypeData themselves.
        :trace: The Trace from the lower branches of the tree of TypeData.\
            Public uses of this method should use the `additional_trace`\
            parameter of the `observe` method instead.
        '''
        if trace is None:
            trace = Trace([name])
        self._trace = trace
        for child, representation, relationship in self.children:
            child.finalize(name, trace.copy(representation, relationship))
        return self

class Key[C, K:Hashable, V, TK=K, TV=V](TypeDatum[C, V, TV]):
    '''
    A TypeDatum that can be used as a key in TypedDatum in place of the value
    type.
    '''

    allows_children_transform = False # because this is a flat TypeDatum.

    __slots__ = (
        "key_transform",
        "name",
        "not_present",
        "required",
        "transform",
        "verify_function",
        "verify_type",
        "why_wrong",
    )

    def __init__(
        self,
        name:K,
        required:SupportsBool,
        verify_type:type[V]|tuple[type[V],...],
        transform:Callable[[V, C],TV]|TypeDatum[C, V, TV]|None=None,
        key_transform:Callable[[K, C],TK]|TypeDatum[C, K, TK]|None=None,
        verify_function:Callable[[Any],TypeIs[V]]|None=None,
        not_present:Callable[[C],TV]|None=None,
        why_wrong:Callable[[Any],str|None]=lambda data: None,
    ) -> None:
        '''
        :name: The key of the dict.
        :required: If this key is required in its parent dict.
        :verify_type: The type of the key's corresponding value.
        :transform: A function called on the value with the transform context\
            or a TypeDatum.
        :key_transform: A function called on the key with the transform\
            context or a TypeDatum.
        :verify_function: An optional function that is called on the value if\
            present. If `False`, an exception will be raised.
        :not_present: If present, will be called if the key is not present.\
            The result is added to the output of the TypedDatum.
        :why_wrong: An optional function called if present and the value fails\
            either `verify_type` or `verify_function`. Should return a string\
            in the form of "because reasons".
        '''
        super().__init__(*([(transform, None, None)] if isinstance(transform, TypeDatum) else []))
        self.name = name
        self.required = bool(required)
        self.verify_type = verify_type
        self.transform = transform
        self.key_transform = key_transform
        self.verify_function = verify_function
        self.not_present = not_present
        self.why_wrong = why_wrong

    def observe(self, data: V, transform_context: C, additional_trace: str) -> tuple[TV|EllipsisType, list[LineType]]:
        if not isinstance(data, self.verify_type):
            return ..., [(0, str(Exceptions.TypeDatumTypeError(self.trace.relationship(additional_trace), type(data), self.verify_type, self.why_wrong(data))))]
        elif self.verify_function is not None and not self.verify_function(data):
            return ..., [(0, str(Exceptions.TypeDatumTypeFunctionError(self.trace.relationship(additional_trace), self.why_wrong(data))))]
        elif isinstance(self.transform, TypeDatum):
            return self.transform.observe(data, transform_context, additional_trace)
        elif self.transform is not None:
            return self.transform(data, transform_context), []
        else:
            # If no transform exists, V=TV.
            return cast(TV, data), []

class TypedDatum[C, K:Hashable, D:Mapping=dict, TK:Hashable=K, TD=D, ](TypeDatum[C, D, TD]):
    '''
    A TypeDatum that can verify and transform any mapping with different values.
    '''

    __slots__ = (
        "data_transform",
        "data_type",
        "data_why_wrong",
        "key_type",
        "key_why_wrong",
        "keys",
        "not_presentable_keys",
        "required_keys",
        "value_type",
        "value_why_wrong",
    )

    def __init__(
        self,
        key_type:type[K]|tuple[type[K],...],
        value_type:type[Any]|tuple[type[Any],...],
        data_type:type[D]|tuple[type[D],...],
        *,
        data_transform:Callable[[dict[TK, Any], C], TD]|None=None,
        keys:list[Key[C, K, any, TK, any]], # type: ignore
        # usage of the wrong Any here FORCES python to BEHAVE CORRECTLY >:(. (forces those TypeVars of Key specifically to be Unknown, allowing them to be inferred via other means.)
        key_why_wrong:Callable[[Any],str|None]=lambda data: None,
        value_why_wrong:Callable[[Any],str|None]=lambda data: None,
        data_why_wrong:Callable[[Any],str|None]=lambda data: None,
    ) -> None:
        '''
        :key_type: The type of the mapping's key.
        :value_type: The type of the mapping's value.
        :data_type: The type of the mapping.
        :data_transform: A function called on the data with the transform\
            context.
        :keys: A list of Key TypeData that represent the keys of this Dict.
        :key_why_wrong: An optional function called if present and a key\
            fails `key_type`. Should return a string in the form of "because\
            reasons".
        :value_why_wrong: An optional function called if present and a value\
            fails `value_type`. Should return a string in the form of "because\
            reasons".
        :data_why_wrong: An optional function called if present and the data\
            fails `data_type`. Should return a string in the form of "because\
            reasons".
        '''
        children:list[tuple[TypeDatum,str|None,str|None]] = []
        if isinstance(data_transform, TypeDatum):
            children.append((data_transform, "data", "data of "))
        if keys is not None:
            children.extend((key, str(key.name), f"key {key.name:r} of ") for key in keys)
        super().__init__(*children)
        self.key_type = key_type
        self.value_type = value_type
        self.data_type = data_type
        self.data_transform = data_transform
        self.keys:dict[K,Key[C, K, Any, TK, Any]] = {key.name: key for key in keys}
        self.key_why_wrong = key_why_wrong
        self.value_why_wrong = value_why_wrong
        self.data_why_wrong = data_why_wrong
        self.required_keys:list[Key[C, K, Any, TK, Any]] = [key for key in keys if key.required]
        self.not_presentable_keys:list[tuple[Key[C, K, Any, TK, Any], Callable[[C], Any]]] = [(key, key.not_present) for key in keys if key.not_present is not None]

    def observe(self, data: D, transform_context: C, additional_trace: str) -> tuple[TD|EllipsisType, list[LineType]]:
        if not isinstance(data, self.data_type):
            return ..., [(0, str(Exceptions.TypeDatumTypeError(self.trace.relationship(additional_trace), type(data), self.data_type, self.data_why_wrong(data))))]
        exceptions:list[LineType] = []
        exceptions.extend(
            (0, str(Exceptions.TypeDatumRequiredKeyMissingErrror(key.trace.relationship(additional_trace))))
            for key in self.required_keys
            if key.name not in data
        )

        output:dict[TK, Any] = {}
        for key_object, not_present in self.not_presentable_keys:
            if key_object.name in data: continue
            if isinstance(key_object.key_transform, TypeDatum):
                transformed_key, new_exceptions = key_object.key_transform.observe(key_object.name, transform_context, additional_trace)
                exceptions.extend(new_exceptions)
            elif key_object.key_transform is not None:
                transformed_key = key_object.key_transform(key_object.name, transform_context)
            else:
                transformed_key = cast(TK, key_object.name)
            if transformed_key is not ...:
                output[transformed_key] = not_present(transform_context)

        for key, value in data.items():
            key = cast(K, key); value = cast(Any, value)
            pair_has_errors:bool = False
            if not isinstance(key, self.key_type):
                exceptions.append((0, str(Exceptions.TypeDatumTypeError(self.trace.relationship(additional_trace, f"key {key:r} of "), type(key), self.key_type, self.key_why_wrong(key)))))
                pair_has_errors = True
            if not isinstance(value, self.value_type):
                exceptions.append((0, str(Exceptions.TypeDatumTypeError(self.trace.relationship(additional_trace, f"value at {key:r} of "), type(value), self.value_type, self.value_why_wrong(value)))))
                pair_has_errors = True
            if pair_has_errors:
                continue

            key_object = self.keys.get(key)
            if key_object is None:
                exceptions.append((0, str(Exceptions.TypeDatumUnrecognizedKeyError(key, self.trace.relationship(additional_trace)))))
                continue

            # key transform
            transformed_key:TK|EllipsisType
            if isinstance(key_object.key_transform, TypeDatum):
                transformed_key, new_exceptions = key_object.key_transform.observe(key, transform_context, additional_trace)
                exceptions.extend(new_exceptions)
            elif key_object.key_transform is not None:
                transformed_key = key_object.key_transform(key, transform_context)
            else:
                transformed_key = cast(TK, key)

            # value transform
            transformed_value:Any|EllipsisType
            if isinstance(key_object, TypeDatum):
                transformed_value, new_exceptions = key_object.observe(value, transform_context, additional_trace)
                exceptions.extend(new_exceptions)
            elif key_object is not None:
                transformed_value = key_object(value, transform_context)
            else:
                transformed_value = cast(Any, value)

            if transformed_key is ... or transformed_value is ...:
                continue
            output[transformed_key] = transformed_value

        if len(exceptions) > 0:
            return ..., exceptions
        elif self.data_transform is not None:
            return self.data_transform(output, transform_context), exceptions
        else:
            return cast(TD, output), exceptions

class Dict[C, K:Hashable, V, D:Mapping=dict, TK:Hashable=K, TV=V, TD=D](TypeDatum[C, D, TD]):
    '''
    A TypeDatum that can verify and transform any mapping with same-type values.
    '''

    __slots__ = (
        "data_transform",
        "data_type",
        "data_why_wrong",
        "key_transform",
        "key_type",
        "key_why_wrong",
        "value_transform",
        "value_type",
        "value_why_wrong",
    )

    def __init__(
        self,
        key_type:type[K]|tuple[type[K],...],
        value_type:type[V]|tuple[type[V],...],
        data_type:type[D]|tuple[type[D],...],
        *,
        key_transform:Callable[[K, C], TK]|TypeDatum[C, K, TK]|None=None,
        value_transform:Callable[[V, C], TV]|TypeDatum[C, V, TV]|None=None,
        data_transform:Callable[[dict[TK, TV], C], TD]|None=None,
        key_why_wrong:Callable[[Any],str|None]=lambda data: None,
        value_why_wrong:Callable[[Any],str|None]=lambda data: None,
        data_why_wrong:Callable[[Any],str|None]=lambda data: None,
    ) -> None:
        '''
        :key_type: The type of the mapping's key.
        :value_type: The type of the mapping's value.
        :data_type: The type of the mapping.
        :key_transform: A function called on each key with the transform\
            context or a TypeDatum.
        :value_transform: A function called on each value with the transform\
            context or a TypeDatum.
        :data_transform: A function called on the data with the transform\
            context.
        :key_why_wrong: An optional function called if present and a key\
            fails `key_type`. Should return a string in the form of "because\
            reasons".
        :value_why_wrong: An optional function called if present and a value\
            fails `value_type`. Should return a string in the form of "because\
            reasons".
        :data_why_wrong: An optional function called if present and the data\
            fails `data_type`. Should return a string in the form of "because\
            reasons".
        '''
        children:list[tuple[TypeDatum,str|None,str|None]] = []
        if isinstance(key_transform, TypeDatum):
            children.append((key_transform, "key", "key of "))
        if isinstance(value_transform, TypeDatum):
            children.append((value_transform, "value", "value of "))
        if isinstance(data_transform, TypeDatum):
            children.append((data_transform, "data", "data of "))
        super().__init__(*children)
        self.key_type = key_type
        self.value_type = value_type
        self.data_type = data_type
        self.key_transform = key_transform
        self.value_transform = value_transform
        self.data_transform = data_transform
        self.key_why_wrong = key_why_wrong
        self.value_why_wrong = value_why_wrong
        self.data_why_wrong = data_why_wrong

    def observe(self, data: D, transform_context: C, additional_trace: str) -> tuple[TD|EllipsisType, list[LineType]]:
        if not isinstance(data, self.data_type):
            return ..., [(0, str(Exceptions.TypeDatumTypeError(self.trace.relationship(additional_trace), type(data), self.data_type, self.data_why_wrong(data))))]
        exceptions:list[LineType] = []

        output:dict[TK, TV] = {}
        for key, value in data.items():
            key = cast(K, key); value = cast(V, value)
            pair_has_errors:bool = False
            if not isinstance(key, self.key_type):
                exceptions.append((0, str(Exceptions.TypeDatumTypeError(self.trace.relationship(additional_trace, f"key {key:r} of "), type(key), self.key_type, self.key_why_wrong(key)))))
                pair_has_errors = True
            if not isinstance(value, self.value_type):
                exceptions.append((0, str(Exceptions.TypeDatumTypeError(self.trace.relationship(additional_trace, f"value at {key:r} of "), type(value), self.value_type, self.value_why_wrong(value)))))
                pair_has_errors = True
            if pair_has_errors:
                continue

            # key transform
            transformed_key:TK|EllipsisType
            if isinstance(self.key_transform, TypeDatum):
                transformed_key, new_exceptions = self.key_transform.observe(key, transform_context, additional_trace)
                exceptions.extend(new_exceptions)
            elif self.key_transform is not None:
                transformed_key = self.key_transform(key, transform_context)
            else:
                transformed_key = cast(TK, key)

            # value transform
            transformed_value:TV|EllipsisType
            if isinstance(self.value_transform, TypeDatum):
                transformed_value, new_exceptions = self.value_transform.observe(value, transform_context, additional_trace)
                exceptions.extend(new_exceptions)
            elif self.value_transform is not None:
                transformed_value = self.value_transform(value, transform_context)
            else:
                transformed_value = cast(TV, value)

            if transformed_key is ... or transformed_value is ...:
                continue
            output[transformed_key] = transformed_value

        if len(exceptions) > 0:
            return ..., exceptions
        elif self.data_transform is not None:
            return self.data_transform(output, transform_context), exceptions
        else:
            return cast(TD, output), exceptions

class Iter[C, I, D:Iterable, TI=I, TD=D](TypeDatum[C, D, TD]):
    '''
    A TypeDatum that verifies and transforms the types of an iterable type.
    '''

    __slots__ = (
        "data_transform",
        "data_type",
        "data_why_wrong",
        "item_transform",
        "item_type",
        "item_why_wrong",
    )

    def __init__(
        self,
        item_type:type[I]|tuple[type[I],...],
        data_type:type[D]|tuple[type[D],...],
        item_transform:Callable[[I, C], TI]|TypeDatum[C, I, TI]|None=None,
        data_transform:Callable[[list[TI], C], TD]|None=None,
        item_why_wrong:Callable[[Any],str|None]=lambda data: None,
        data_why_wrong:Callable[[Any],str|None]=lambda data: None,
    ) -> None:
        '''
        :item_type: The type of the iterable's item.
        :data_type: The type of the iterable.
        :item_transform: A function called on each item with the transform\
            context or a TypeDatum.
        :data_transform: A function called on the data with the transform\
            context.
        :item_why_wrong: An optional function called if present and an item\
            fails `item_type`. Should return a string in the form of "because\
            reasons".
        :data_why_wrong: An optional function called if present and the data\
            fails `data_type`. Should return a string in the form of "because\
            reasons".
        '''
        super().__init__(*([(item_transform, "item", "item of ")] if isinstance(item_transform, TypeDatum) else []))
        self.item_type = item_type
        self.data_type = data_type
        self.item_transform = item_transform
        self.data_transform = data_transform
        self.item_why_wrong = item_why_wrong
        self.data_why_wrong = data_why_wrong

    def observe(self, data: D, transform_context: C, additional_trace: str) -> tuple[TD | EllipsisType, Iterable[LineType]]:
        if not isinstance(data, self.data_type):
            return ..., [(0, str(Exceptions.TypeDatumTypeError(self.trace.relationship(additional_trace), type(data), self.data_type)))]
        exceptions:list[LineType] = []
        output:list[TI] = []
        for index, item in enumerate(data):
            item = cast(I, item)
            if not isinstance(item, self.item_type):
                exceptions.append((0, str(Exceptions.TypeDatumTypeError(self.trace.relationship(additional_trace, f"item {index:i} of "), type(item), self.item_type))))
                continue
            transformed_item:TI|EllipsisType
            if isinstance(self.item_transform, TypeDatum):
                transformed_item, new_exceptions = self.item_transform.observe(item, transform_context, additional_trace)
                exceptions.extend(new_exceptions)
            elif self.item_transform is not None:
                transformed_item = self.item_transform(item, transform_context)
            else:
                transformed_item = cast(TI, item)

            if transformed_item is ...:
                continue
            output.append(transformed_item)

        if len(exceptions) > 0:
            return ..., exceptions
        elif self.data_transform is not None:
            return self.data_transform(output, transform_context), exceptions
        else:
            return cast(TD, output), exceptions

class EnumDatum[C, D, TD=D](TypeDatum[C, D, TD]):
    '''
    TypeDatum for verifying data using a callable or Container.
    '''

    __slots__ = (
        "collection",
        "transform",
        "why_wrong",
    )

    def __init__(
        self,
        collection:Container[D]|Callable[[Any],TypeIs[D]],
        transform:Callable[[D, C], TD]|TypeDatum[C, D, TD]|None=None,
        why_wrong:Callable[[Any],str|None]=lambda data: None,
    ) -> None:
        '''
        :collection: A container or callable that verifies that the data is\
            correct.
        :transform: A function called on each item with the transform\
            context or a TypeDatum.
        :why_wrong: An optional function called if present and the data fails\
            `collection`. Should return a string in the form of "because\
            reasons".
        '''
        super().__init__(*([transform, None, None] if isinstance(transform, TypeDatum) else []))
        self.collection = collection
        self.transform = transform
        self.why_wrong = why_wrong

    def observe(self, data: D, transform_context: C, additional_trace: str) -> tuple[TD | EllipsisType, list[LineType]]:
        if isinstance(self.collection, Container) and data not in self.collection:
            return ..., [(0, str(Exceptions.EnumDatumFailureError(self.trace.relationship(additional_trace), self.why_wrong(data))))]
        elif callable(self.collection) and not self.collection(data):
            return ..., [(0, str(Exceptions.EnumDatumFailureError(self.trace.relationship(additional_trace), self.why_wrong(data))))]
        elif isinstance(self.transform, TypeDatum):
            return self.transform.observe(data, transform_context, additional_trace)
        elif self.transform is not None:
            return self.transform(data, transform_context), []
        else:
            return cast(TD, data), []

class UnionDatum[C, D, TD](TypeDatum[C, D, TD]):
    '''
    Allows for branching TypeData.
    '''

    __slots__ = (
        "split",
        "why_wrong"
    )

    def __init__(
        self,
        *split:TypeDatum[C, D, TD],
        why_wrong:Callable[[Any],str|None]=lambda data: None,
    ) -> None:
        '''
        :split: The TypeData that this Union can be. Place them in order of\
            most to least likely.
        :why_wrong: An optional function called if present and the data fails\
            all branches. Should return a string in the form of "because\
            reasons".
        '''
        super().__init__(*((transform, str(index), f"branch {index} of ") for index, transform in enumerate(split)))
        self.split = split
        self.why_wrong = why_wrong

    def observe(self, data: D, transform_context: C, additional_trace: str) -> tuple[TD | EllipsisType, list[tuple[int, str]]]:
        branches:list[list[tuple[int,str]]] = []
        for transform in self.split:
            output, new_exceptions = transform.observe(data, transform_context, additional_trace)
            if output is ...:
                branches.append(new_exceptions)
            else:
                return output, new_exceptions
        message = self.why_wrong(data)
        exceptions:list[LineType] = []
        for index, branch in enumerate(branches):
            exceptions.append((0, str(Exceptions.UnionDatumFailedError(self.trace.relationship(additional_trace, f"branch {index} of "), message))))
            exceptions.extend((indentation + 1, line) for indentation, line in branch)
        return ..., exceptions

class Simple[C, D, TD=D](TypeDatum[C, D, TD]):
    '''
    Simple TypeDatum that only verifies the type.
    '''

    __slots__ = (
        "transform",
        "verify_type",
        "why_wrong",
    )

    def __init__(
        self,
        verify_type:type[D]|tuple[type[D],...],
        transform:Callable[[D, C], TD]|None=None,
        why_wrong:Callable[[Any],str|None]=lambda data: None,
    ) -> None:
        '''
        :verify_type: The type that the data must be.
        :transform: A function called on each item with the transform\
            context.
        :why_wrong: An optional function called if present and the data fails\
            `verify_type`. Should return a string in the form of "because\
            reasons".
        '''
        super().__init__()
        self.verify_type = verify_type
        self.transform = transform
        self.why_wrong = why_wrong

    def observe(self, data: D, transform_context: C, additional_trace: str) -> tuple[TD | EllipsisType, list[tuple[int, str]]]:
        if not isinstance(data, self.verify_type):
            return ..., [(0, str(Exceptions.TypeDatumTypeError(self.trace.relationship(additional_trace), type(data), self.verify_type)))]
        elif self.transform is not None:
            return self.transform(data, transform_context), []
        else:
            return cast(TD, data), []
