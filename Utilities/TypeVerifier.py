import enum
from typing import Any, Callable, Container, Hashable, Mapping, Sequence

import Utilities.Exceptions as Exceptions
from Utilities.Trace import Trace


class TraceItemType(enum.Enum):
    KEY = 0
    ITEM = 1
    VALUE = 2
    OTHER = 3

class TypeVerifier[A]():
    '''Use `base_verify` to check the types of data.'''

    __slots__ = ()

    def get_type_str(self, types:"type|tuple[type,...]|TypeVerifier|tuple[type|TypeVerifier,...]") -> str:
        if not isinstance(types, tuple):
            types = (types,)
        output:list[str] = []
        for item in types:
            match item:
                case type():
                    output.append(item.__name__)
                case TypeVerifier():
                    data_types = item.get_data_type()
                    if isinstance(data_types, type):
                        output.append(data_types.__name__)
                    else:
                        output.extend(_type.__name__ for _type in data_types)
        return ", ".join(output)

    def get_data_type(self) -> type|tuple[type,...]:
        ...

    def verify(self, data:A, trace:Trace) -> bool: ... # returns True if there are new exceptions.

    def verify_throw(self, data:A, trace_items:tuple[Any,...]|None=None) -> None:
        '''
        Verifies data and immediately raises any exceptions.
        '''
        trace = Trace()
        if trace_items is None:
            trace_items = ("data",)
        with trace.enter_keys(trace_items, data):
            has_exceptions = self.verify(data, trace)
        if has_exceptions:
            for text in trace.stringify():
                print(text)
            raise Exceptions.TypeVerificationFailedError(self)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

class DictTypeVerifier[K: Hashable, V](TypeVerifier[Mapping[K, V]]):

    __slots__ = (
        "additional_function",
        "data_type",
        "key_function",
        "key_type",
        "value_function",
        "value_type",
    )

    def __init__(
            self,
            data_type:type[Mapping]|tuple[type[Mapping],...],
            key_type:type[K]|tuple[type[K],...]|TypeVerifier[K],
            value_type:type[V]|tuple[type[V],...]|TypeVerifier[V],
            key_function:Callable[[K, V],tuple[bool,str|None]]|None=None,
            value_function:Callable[[K, V],tuple[bool,str|None]]|None=None,
            additional_function:Callable[[Mapping[K, V]],tuple[bool,str|None]]|None=None,
        ) -> None:
        self.key_type = key_type
        self.value_type = value_type
        self.data_type = data_type
        self.key_function = key_function
        self.value_function = value_function
        self.additional_function = additional_function

    def get_data_type(self) -> type | tuple[type, ...]:
        return self.data_type

    def verify(self, data: Mapping[K, V], trace:Trace) -> bool:
        if not isinstance(data, self.data_type):
            trace.exception(Exceptions.TypeVerificationTypeError(self.get_type_str(self.data_type), type(data)))
            return True
        exceptions_exist:bool = False
        for index, (key, value) in enumerate(data.items()):
            with trace.enter_key(key, value):
                if isinstance(self.key_type, TypeVerifier):
                    if self.key_type.verify(key, trace):
                        exceptions_exist = True
                        continue
                else:
                    if not isinstance(key, self.key_type):
                        trace.exception(Exceptions.TypeVerificationTypeError(self.get_type_str(self.key_type), type(key)))
                        exceptions_exist = True
                        continue
                if isinstance(self.value_type, TypeVerifier):
                    if self.value_type.verify(value, trace):
                        exceptions_exist = True
                        continue
                else:
                    if not isinstance(value, self.value_type):
                        trace.exception(Exceptions.TypeVerificationTypeError(self.get_type_str(self.value_type), type(value)))
                        exceptions_exist = True
                        continue
                if self.key_function is not None:
                    key_function_success, key_function_message = self.key_function(key, value)
                    if not key_function_success:
                        trace.exception(Exceptions.TypeVerificationFunctionError(key_function_message))
                        exceptions_exist = True
                        continue
                if self.value_function is not None:
                    value_function_success, value_function_message = self.value_function(key, value)
                    if not value_function_success:
                        trace.exception(Exceptions.TypeVerificationFunctionError(value_function_message))
                        exceptions_exist = True
                        continue
        if exceptions_exist:
            return True
        if self.additional_function is not None:
            additional_function_success, additional_function_message = self.additional_function(data)
            if not additional_function_success:
                trace.exception(Exceptions.TypeVerificationFunctionError(additional_function_message))
                return True
        return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id {id(self)}>"

class TypedDictKeyTypeVerifier[K: Hashable, V](TypeVerifier[tuple[K, V]]):

    __slots__ = (
        "function",
        "key",
        "required",
        "value_type",
    )

    def __init__(
            self,
            key:K,
            required:bool,
            value_type:type[V]|tuple[type[V],...]|TypeVerifier[V],
            function:Callable[[K, V],tuple[bool,str|None]]|None=None,
        ) -> None:
        self.key = key
        self.value_type = value_type
        self.required = required
        self.function = function

    def get_data_type(self) -> type | tuple[type, ...]:
        return self.value_type.get_data_type() if isinstance(self.value_type, TypeVerifier) else self.value_type

    def verify(self, data:tuple[K, V], trace:Trace) -> bool:
        key, value = data
        if isinstance(self.value_type, TypeVerifier):
            if self.value_type.verify(value, trace):
                return True
        else:
            if not isinstance(value, self.value_type):
                trace.exception(Exceptions.TypeVerificationTypeError(self.get_type_str(self.value_type), type(value)))
                return True
        if self.function is not None:
            function_success, function_message = self.function(key, value)
            if not function_success:
                trace.exception(Exceptions.TypeVerificationFunctionError(function_message))
                return True
        return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.key} id {id(self)}>"

class TypedDictTypeVerifier[K: Hashable, V](TypeVerifier[Mapping[K, V]]):

    __slots__ = (
        "data_type",
        "function",
        "keys_dict",
        "loose",
        "required_keys"
    )

    def __init__(
            self,
            *keys:TypedDictKeyTypeVerifier,
            data_type:type[Mapping]|tuple[type[Mapping],...]=dict,
            function:Callable[[Mapping[K, V]],tuple[bool,str|None]]|Any|None=None,
            loose:bool=False,
        ) -> None:
        self.keys_dict = {key.key: key for key in keys}
        self.data_type = data_type
        self.function = function
        self.loose = loose

        self.required_keys = [key.key for key in keys if key.required]

    def get_data_type(self) -> type | tuple[type, ...]:
        return self.data_type

    def verify(self, data: Mapping[Any, Any], trace:Trace) -> bool:
        if not isinstance(data, self.data_type):
            trace.exception(Exceptions.TypeVerificationTypeError(self.get_type_str(self.data_type), type(data)))
            return True
        exceptions_exist:bool = False
        for key, value in data.items():
            with trace.enter_key(key, value):
                type_verifier = self.keys_dict.get(key)
                if type_verifier is None:
                    if not self.loose:
                        trace.exception(Exceptions.TypeVerificationUnrecognizedKeyError(key, [key for key in self.keys_dict.keys() if key not in data]))
                        exceptions_exist = True
                    continue
                if type_verifier.verify((key, value), trace):
                    exceptions_exist = True
                    continue
        for required_key in self.required_keys:
            with trace.enter_key(required_key, ...):
                if required_key not in data:
                    trace.exception(Exceptions.TypeVerificationMissingKeyError(required_key))
                    exceptions_exist = True
                    continue
        if exceptions_exist:
            return True
        if self.function is not None:
            function_success, function_message = self.function(data)
            if not function_success:
                trace.exception(Exceptions.TypeVerificationFunctionError(function_message))
                return True
        return False

    def extend(self, other:"TypedDictTypeVerifier") -> "TypedDictTypeVerifier":
        '''
        Modifies other by combining itself with `self`.
        '''
        if other.function is None and self.function is None:
            function = None
        elif other.function is None and self.function is not None:
            function = self.function
        elif other.function is not None and self.function is None:
            function = other.function
        elif other.function is not None and self.function is not None:
            function1 = other.function
            function2 = self.function
            def combine_functions(data:Mapping) -> tuple[bool, str|None]:
                result1, message1 = function1(data)
                if result1:
                    return result1, message1
                return function2(data)
            function = combine_functions
        else: assert False # idk why this is necessary either
        other.function = function
        if len(overlap_keys := other.keys_dict.keys() & self.keys_dict) > 0:
            raise Exceptions.TypedDictTypeVerifierKeysOverlapError(other, self, sorted(overlap_keys))
        other.keys_dict.update(self.keys_dict)
        other.required_keys.extend(self.required_keys)
        other.loose = other.loose or self.loose
        self_data_type = list(other.data_type) if isinstance(other.data_type, tuple) else [other.data_type]
        other_data_type = list(self.data_type) if isinstance(self.data_type, tuple) else [self.data_type]
        other.data_type = tuple(self_data_type + other_data_type)
        return other

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id {id(self)} ({", ".join(self.keys_dict)})>"

class ListTypeVerifier[I](TypeVerifier[Sequence[I]]):

    __slots__ = (
        "additional_function",
        "data_type",
        "item_function",
        "item_type",
        "item_type_is_verifier",
    )

    def __init__(
            self,
            item_type:type[I]|tuple[type[I],...]|TypeVerifier[I],
            data_type:type[Sequence]|tuple[type[Sequence],...],
            item_function:Callable[[I],tuple[bool,str|None]]|None=None,
            additional_function:Callable[[Sequence[I]],tuple[bool,str|None]]|None=None,
        ) -> None:
        self.item_type = item_type
        self.data_type = data_type
        self.item_function = item_function
        self.additional_function = additional_function

    def get_data_type(self) -> type | tuple[type, ...]:
        return self.data_type

    def verify(self, data: Sequence[I], trace:Trace) -> bool:
        if not isinstance(data, self.data_type):
            trace.exception(Exceptions.TypeVerificationTypeError(self.get_type_str(self.data_type), type(data)))
            return True
        exceptions_exist:bool = False
        for index, item in enumerate(data):
            with trace.enter_key(index, item):
                if isinstance(self.item_type, TypeVerifier):
                    if self.item_type.verify(item, trace):
                        exceptions_exist = True
                        continue
                else:
                    if not isinstance(item, self.item_type):
                        trace.exception(Exceptions.TypeVerificationTypeError(self.get_type_str(self.item_type), type(item)))
                        exceptions_exist = True
                        continue
                if self.item_function is not None:
                    item_function_success, item_function_message = self.item_function(item)
                    if not item_function_success:
                        trace.exception(Exceptions.TypeVerificationFunctionError(item_function_message))
                        exceptions_exist = True
                        continue
        if exceptions_exist:
            return True
        if self.additional_function is not None:
            additional_function_success, additional_function_message = self.additional_function(data)
            if not additional_function_success:
                trace.exception(Exceptions.TypeVerificationFunctionError(additional_function_message))
                return True
        return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id {id(self)}>"

class EnumTypeVerifier[I](TypeVerifier[I]):

    __slots__ = (
        "options",
    )

    def __init__(self, options:Container[I]) -> None:
        self.options = options

    def get_data_type(self) -> type | tuple[type, ...]:
        data_types_set:set[type] = set()
        data_types_list:list[type] = []
        for option in self.options: # type: ignore
            if type(option) not in data_types_set:
                data_types_set.add(type(option))
                data_types_list.append(type(option))
        return data_types_list[0] if len(data_types_list) == 0 else tuple(data_types_list)

    def verify(self, data: I, trace:Trace) -> bool:
        if data not in self.options:
            trace.exception(Exceptions.TypeVerificationEnumError(self.options, data))
            return True
        return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.options}>"

class UnionTypeVerifier[I](TypeVerifier[I]):

    __slots__ = (
        "types",
        "types_are_type_verifiers",
    )

    def __init__(self, *types:type[I]|TypeVerifier[I]|Any) -> None:
        self.types = types
        self.types_are_type_verifiers = [isinstance(type, TypeVerifier) for type in types]

    def get_data_type(self) -> type | tuple[type, ...]:
        data_types_set:set[type] = set()
        data_types_list:list[type] = []
        for _type in self.types:
            types:tuple[type,...]
            match _type:
                case type():
                    types = (_type,)
                case TypeVerifier():
                    tepes = _type.get_data_type()
                    types = (tepes,) if isinstance(tepes, type) else tepes
                case _:
                    types = ()
            for data_type in types:
                if data_type not in data_types_set:
                    data_types_set.add(data_type)
                    data_types_list.append(data_type)
        return data_types_list[0] if len(data_types_list) == 0 else tuple(data_types_list)

    def verify(self, data: I, trace: Trace) -> bool:
        subtraces:list[Trace] = [] # Union expects exceptions to exist. It only needs some of them.
        for type_verifier, is_type_verifier in zip(self.types, self.types_are_type_verifiers):
            if isinstance(type_verifier, TypeVerifier):
                subtrace = Trace()
                if not type_verifier.verify(data, subtrace):
                    return False
                else:
                    subtraces.append(subtrace)
            else:
                if isinstance(data, type_verifier):
                    return False
        else:
            exception_count:int = 0
            for subtrace in subtraces:
                exception_count += len(subtrace)
                trace.include(subtrace)
            trace.exception(Exceptions.TypeVerificationUnionError(self.get_type_str(self.types), type(data), exception_count))
            return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id {id(self)}>"
