import enum
import traceback
from typing import (Any, Callable, Container, Hashable, Iterable, Mapping,
                    Self, Sequence, cast)

import Utilities.Exceptions as Exceptions


class TraceItemType(enum.Enum):
    KEY = 0
    ITEM = 1
    VALUE = 2
    OTHER = 3

class StackTrace():

    __slots__ = (
        "trace",
    )

    def __init__(self, trace:list[tuple[object, TraceItemType]]|None=None) -> None:
        self.trace = [] if trace is None else trace

    def enter(self, index:object, index_type:TraceItemType) -> Self:
        self.trace.append((index, index_type))
        return self

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc) -> None:
        self.trace.pop()

    def copy(self, index:object, index_type:TraceItemType) -> "StackTrace":
        return StackTrace(self.trace.copy()).enter(index, index_type)

    def to_str(self, capitalize:bool=True) -> str:
        result:list[str] = []
        for item_index, (index, index_type) in enumerate(reversed(self.trace)):
            match index_type:
                case TraceItemType.KEY:
                    item = f"key \"{index}\" of "
                case TraceItemType.VALUE:
                    item = f"value of \"{index}\" of "
                case TraceItemType.ITEM:
                    item = f"item {index} of"
                case TraceItemType.OTHER:
                    item = f"{index} of "
            result.append(item.capitalize() if item_index == 0 and capitalize else item)
        result.append("data")
        return "".join(result)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} len {len(self.trace)}>"


def make_trace(trace_items:list[Any]|None) -> StackTrace:
    trace_items_final:list[tuple[object,TraceItemType]]|None = [(trace_item, TraceItemType.OTHER) for trace_item in trace_items] if trace_items is not None else None
    return StackTrace(trace_items_final)

class TypeVerifier[A]():
    '''Use `base_verify` to check the types of data.'''

    def verify(self, data:A, trace:StackTrace) -> list[Exceptions.TypeVerificationTypeException]: ...

    def base_verify(self, data:A, trace_items:list[Any]|None=None) -> None:
        exceptions = self.verify(data, make_trace(trace_items))
        if len(exceptions) > 0:
            for exception in exceptions:
                traceback.print_exception(exception)
            raise Exceptions.TypeVerificationFailedError(self)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

class DictTypeVerifier[K: Hashable, V](TypeVerifier[Mapping[K, V]]):

    __slots__ = (
        "additional_function",
        "data_type",
        "data_type_str",
        "key_function",
        "key_type",
        "key_type_is_verifier",
        "key_type_str",
        "value_function",
        "value_type",
        "value_type_is_verifier",
        "value_type_str",
    )

    def __init__(
            self,
            data_type:type[Mapping]|tuple[type[Mapping],...],
            key_type:type[K]|tuple[type[K],...]|TypeVerifier[K],
            value_type:type[V]|tuple[type[V],...]|TypeVerifier[V],
            data_type_str:str,
            key_type_str:str,
            value_type_str:str,
            key_function:Callable[[K, V],tuple[bool,str|None]]|None=None,
            value_function:Callable[[K, V],tuple[bool,str|None]]|None=None,
            additional_function:Callable[[Mapping[K, V]],tuple[bool,str|None]]|None=None,
        ) -> None:
        self.key_type = key_type
        self.key_type_is_verifier = isinstance(key_type, TypeVerifier)
        self.value_type = value_type
        self.value_type_is_verifier = isinstance(value_type, TypeVerifier)
        self.data_type = data_type
        self.key_type_str = key_type_str
        self.value_type_str = value_type_str
        self.data_type_str = data_type_str
        self.key_function = key_function
        self.value_function = value_function
        self.additional_function = additional_function

    def verify(self, data: Mapping[K, V], trace:StackTrace) -> list[Exceptions.TypeVerificationTypeException]:
        exceptions:list[Exceptions.TypeVerificationTypeException] = []
        if not isinstance(data, self.data_type):
            exceptions.append(Exceptions.TypeVerificationTypeError(trace, self.data_type_str, type(data)))
            return exceptions
        for index, (key, value) in enumerate(data.items()):
            if self.key_type_is_verifier:
                with trace.enter(key, TraceItemType.KEY) as subtrace:
                    new_exceptions = cast(TypeVerifier, self.key_type).verify(key, subtrace)
                if new_exceptions:
                    exceptions.extend(new_exceptions)
                    continue
            else:
                if not isinstance(key, self.key_type): # type: ignore
                    exceptions.append(Exceptions.TypeVerificationTypeError(trace.copy(index, TraceItemType.ITEM), self.key_type_str, type(key)))
                    continue
            if self.value_type_is_verifier:
                with trace.enter(key, TraceItemType.VALUE) as subtrace:
                    new_exceptions = cast(TypeVerifier, self.value_type).verify(value, subtrace)
                if new_exceptions:
                    exceptions.extend(new_exceptions)
                    continue
            else:
                if not isinstance(value, self.value_type): # type: ignore
                    exceptions.append(Exceptions.TypeVerificationTypeError(trace.copy(index, TraceItemType.VALUE), self.value_type_str, type(value)))
                    continue
            if self.key_function is not None:
                key_function_success, key_function_message = self.key_function(key, value)
                if not key_function_success:
                    exceptions.append(Exceptions.TypeVerificationFunctionError(trace.copy(key, TraceItemType.KEY), key_function_message))
                    continue
            if self.value_function is not None:
                value_function_success, value_function_message = self.value_function(key, value)
                if not value_function_success:
                    exceptions.append(Exceptions.TypeVerificationFunctionError(trace.copy(key, TraceItemType.VALUE), value_function_message, data=value))
                    continue
        if exceptions:
            return exceptions
        if self.additional_function is not None:
            additional_function_success, additional_function_message = self.additional_function(data)
            if not additional_function_success:
                exceptions.append(Exceptions.TypeVerificationFunctionError(trace, additional_function_message, data))
        return exceptions

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} \"{self.key_type_str}\", \"{self.value_type_str}\", \"{self.data_type_str}\">"

class TypedDictKeyTypeVerifier[K: Hashable, V](TypeVerifier[tuple[K, V]]):

    __slots__ = (
        "function",
        "key",
        "required",
        "value_type",
        "value_type_is_verifier",
        "value_type_str",
    )

    def __init__(
            self,
            key:K,
            value_str:str,
            required:bool,
            value_type:type[V]|tuple[type[V],...]|TypeVerifier[V],
            function:Callable[[K, V],tuple[bool,str|None]]|None=None,
        ) -> None:
        self.key = key
        self.value_type = value_type
        self.value_type_is_verifier = isinstance(value_type, TypeVerifier)
        self.value_type_str = value_str
        self.required = required
        self.function = function

    def verify(self, data:tuple[K, V], trace:StackTrace) -> list[Exceptions.TypeVerificationTypeException]:
        exceptions:list[Exceptions.TypeVerificationTypeException] = []
        key, value = data
        if self.value_type_is_verifier:
            with trace.enter(key, TraceItemType.VALUE) as subtrace:
                new_exceptions = cast(TypeVerifier, self.value_type).verify(value, subtrace)
            if new_exceptions:
                exceptions.extend(new_exceptions)
                return exceptions
        else:
            if not isinstance(value, self.value_type): # type: ignore
                exceptions.append(Exceptions.TypeVerificationTypeError(trace.copy(key, TraceItemType.VALUE), self.value_type_str, type(value)))
                return exceptions
        if self.function is not None:
            function_success, function_message = self.function(key, value)
            if not function_success:
                exceptions.append(Exceptions.TypeVerificationFunctionError(trace.copy(key, TraceItemType.KEY), function_message, value))
                return exceptions
        return exceptions

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.key} \"{self.value_type_str}\">"

class TypedDictTypeVerifier[K: Hashable, V](TypeVerifier[Mapping[K, V]]):

    __slots__ = (
        "data_type",
        "data_type_str",
        "function",
        "keys_dict",
        "loose",
        "required_keys"
    )

    def __init__(
            self,
            *keys:TypedDictKeyTypeVerifier,
            data_type:type[Mapping]|tuple[type[Mapping],...]=dict,
            data_type_str:str="a dict",
            function:Callable[[Mapping[K, V]],tuple[bool,str|None]]|None=None,
            loose:bool=False,
        ) -> None:
        self.keys_dict = {key.key: key for key in keys}
        self.data_type = data_type
        self.data_type_str = data_type_str
        self.function = function
        self.loose = loose

        self.required_keys = [key.key for key in keys if key.required]

    def verify(self, data: Mapping[Any, Any], trace:StackTrace) -> list[Exceptions.TypeVerificationTypeException]:
        exceptions:list[Exceptions.TypeVerificationTypeException] = []
        if not isinstance(data, self.data_type):
            exceptions.append(Exceptions.TypeVerificationTypeError(trace, self.data_type_str, type(data)))
            return exceptions
        for key, value in data.items():
            type_verifier = self.keys_dict.get(key)
            if type_verifier is None:
                if not self.loose:
                    exceptions.append(Exceptions.TypeVerificationUnrecognizedKeyError(trace.copy(key, TraceItemType.KEY)))
                continue
            new_exceptions = type_verifier.verify((key, value), trace)
            if new_exceptions:
                exceptions.extend(new_exceptions)
                continue
        for required_key in self.required_keys:
            if required_key not in data:
                exceptions.append(Exceptions.TypeVerificationMissingKeyError(trace.copy(required_key, TraceItemType.KEY)))
                continue
        if exceptions:
            return exceptions
        if self.function is not None:
            function_success, function_message = self.function(data)
            if not function_success:
                exceptions.append(Exceptions.TypeVerificationFunctionError(trace, function_message, data))
        return exceptions

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} \"{self.data_type_str}\" ({", ".join(self.keys_dict)})>"

class ListTypeVerifier[I](TypeVerifier[Sequence[I]]):

    __slots__ = (
        "additional_function",
        "data_type",
        "data_type_str",
        "item_function",
        "item_type",
        "item_type_is_verifier",
        "item_type_str",
    )

    def __init__(
            self,
            item_type:type[I]|tuple[type[I],...]|TypeVerifier[I],
            data_type:type[Sequence]|tuple[type[Sequence],...],
            item_type_str:str,
            data_type_str:str,
            item_function:Callable[[I],tuple[bool,str|None]]|None=None,
            additional_function:Callable[[Sequence[I]],tuple[bool,str|None]]|None=None,
        ) -> None:
        self.item_type = item_type
        self.item_type_is_verifier = isinstance(item_type, TypeVerifier)
        self.data_type = data_type
        self.item_type_str = item_type_str
        self.data_type_str = data_type_str
        self.item_function = item_function
        self.additional_function = additional_function

    def verify(self, data: Sequence[I], trace:StackTrace) -> list[Exceptions.TypeVerificationTypeException]:
        exceptions:list[Exceptions.TypeVerificationTypeException] = []
        if not isinstance(data, self.data_type):
            exceptions.append(Exceptions.TypeVerificationTypeError(trace, self.data_type_str, type(data)))
            return exceptions
        for index, item in enumerate(data):
            if self.item_type_is_verifier:
                with trace.enter(index, TraceItemType.ITEM) as subtrace:
                    new_exceptions = cast(TypeVerifier, self.item_type).verify(item, subtrace)
                if new_exceptions:
                    exceptions.extend(new_exceptions)
                    continue
            else:
                if not isinstance(item, self.item_type): # type: ignore
                    exceptions.append(Exceptions.TypeVerificationTypeError(trace.copy(index, TraceItemType.ITEM), self.item_type_str, type(item)))
                    continue
            if self.item_function is not None:
                item_function_success, item_function_message = self.item_function(item)
                if not item_function_success:
                    exceptions.append(Exceptions.TypeVerificationFunctionError(trace.copy(index, TraceItemType.ITEM), item_function_message, item))
        if exceptions:
            return exceptions
        if self.additional_function is not None:
            additional_function_success, additional_function_message = self.additional_function(data)
            if not additional_function_success:
                exceptions.append(Exceptions.TypeVerificationFunctionError(trace, additional_function_message, data))
        return exceptions

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} \"{self.item_type_str}\" \"{self.data_type_str}\">"

class IterableTypeVerifier[I](ListTypeVerifier):

    __slots__ = ()

    def __init__(
            self,
            item_type:type[I]|tuple[type[I],...]|TypeVerifier[I],
            data_type:type[Iterable]|tuple[type[Iterable],...],
            item_type_str:str,
            data_type_str:str,
            item_function:Callable[[I],tuple[bool,str|None]]|None=None,
            additional_function:Callable[[Iterable[I]],tuple[bool,str|None]]|None=None,
        ) -> None:
        return super().__init__(item_type, cast(type[Sequence]|tuple[type[Sequence],...], data_type), item_type_str, data_type_str, item_function, additional_function)

    def verify(self, data: Iterable[I], trace:StackTrace) -> list[Exceptions.TypeVerificationTypeException]:
        return super().verify(cast(Sequence[I], data), trace)

class EnumTypeVerifier[I](TypeVerifier[I]):

    __slots__ = (
        "options",
    )

    def __init__(self, options:Container[I]) -> None:
        self.options = options

    def verify(self, data: I, trace:StackTrace) -> list[Exceptions.TypeVerificationTypeException]:
        exceptions:list[Exceptions.TypeVerificationTypeException] = []
        if data not in self.options:
            exceptions.append(Exceptions.TypeVerificationEnumError(trace, self.options, data))
        return exceptions

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.options}>"

class UnionTypeVerifier[I](TypeVerifier[I]):

    __slots__ = (
        "type_str",
        "types",
        "types_are_type_verifiers",
    )

    def __init__(self, type_str:str, *types:type[I]|TypeVerifier[I]|Any) -> None:
        self.types = types
        self.types_are_type_verifiers = [isinstance(type, TypeVerifier) for type in types]
        self.type_str = type_str

    def verify(self, data: I, trace: StackTrace) -> list[Exceptions.TypeVerificationTypeException]:
        exceptions:list[Exceptions.TypeVerificationTypeException] = []
        union_exceptions:list[list[Exceptions.TypeVerificationTypeException]] = []
        for type_verifier, is_type_verifier in zip(self.types, self.types_are_type_verifiers):
            if is_type_verifier:
                new_exceptions = cast(TypeVerifier, type_verifier).verify(data, trace)
                if not new_exceptions: return []
                else: union_exceptions.append(new_exceptions)
            else:
                if isinstance(data, type_verifier): # type: ignore
                    return []
        else:
            exceptions.append(Exceptions.TypeVerificationUnionError(trace, self.type_str, type(data), union_exceptions))
        return exceptions

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} \"{self.type_str}\">"
