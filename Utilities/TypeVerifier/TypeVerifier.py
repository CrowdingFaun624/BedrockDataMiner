import enum
import traceback
from typing import (Any, Callable, Container, Generic, Iterable, Mapping,
                    Sequence, TypeVar, cast)

import Utilities.Exceptions as Exceptions

TYPE_CHECK_TYPE_VERIFIERS = False

class TraceItemType(enum.Enum):
    KEY = 0
    ITEM = 1
    VALUE = 2
    OTHER = 3

class Trace():
    def __init__(self, trace:list[tuple[object, TraceItemType]]|None=None) -> None:
        self.trace = [] if trace is None else trace

    def copy(self, index:object, index_type:TraceItemType) -> "Trace":
        new_trace = self.trace.copy()
        new_trace.append((index, index_type))
        return Trace(new_trace)

    def to_str(self, capitalize:bool=True) -> str:
        result = ""
        for item_index, (index, index_type) in enumerate(reversed(self.trace)):
            index_is_capitalized = item_index == 0 and capitalize
            match index_type:
                case TraceItemType.KEY:
                    if index_is_capitalized:
                        result += "Key \"%s\" of " % (index)
                    else:
                        result += "key \"%s\" of " % (index)
                case TraceItemType.VALUE:
                    if index_is_capitalized:
                        result += "Value of \"%s\" of " % (index)
                    else:
                        result += "value of \"%s\" of " % (index)
                case TraceItemType.ITEM:
                    if index_is_capitalized:
                        result += "Item %s of " % (index)
                    else:
                        result += "item %s of " % (index)
                case TraceItemType.OTHER:
                    result += "%s of " % (index)
        result += "data"
        return result

    def __repr__(self) -> str:
        return "<%s len %i>" % (self.__class__.__name__, len(self.trace))


def make_trace(trace_items:list[Any]|None) -> Trace:
    trace_items_final:list[tuple[object,TraceItemType]]|None = [(trace_item, TraceItemType.OTHER) for trace_item in trace_items] if trace_items is not None else None
    return Trace(trace_items_final)

type_verifier_typevar = TypeVar("type_verifier_typevar")
class TypeVerifier(Generic[type_verifier_typevar]):
    '''Use `base_verify` to check the types of data.'''

    def verify(self, data:type_verifier_typevar, trace:Trace) -> list[Exceptions.TypeVerificationTypeException]: ...

    def base_verify(self, data:type_verifier_typevar, trace_items:list[Any]|None=None) -> None:
        exceptions = self.verify(data, make_trace(trace_items))
        if len(exceptions) > 0:
            for exception in exceptions:
                traceback.print_exception(exception)
            raise Exceptions.TypeVerificationFailedError(self)

    def __repr__(self) -> str:
        return "<%s>" % (self.__class__.__name__)

key_typevar = TypeVar("key_typevar")
value_typevar = TypeVar("value_typevar")
item_typevar = TypeVar("item_typevar")

class DictTypeVerifier(TypeVerifier[Mapping[key_typevar, value_typevar]]):

    def __init__(
            self,
            data_type:type[Mapping]|tuple[type[Mapping],...],
            key_type:type[key_typevar]|tuple[type[key_typevar],...]|TypeVerifier[key_typevar],
            value_type:type[value_typevar]|tuple[type[value_typevar],...]|TypeVerifier[value_typevar],
            data_type_str:str,
            key_type_str:str,
            value_type_str:str,
            key_function:Callable[[key_typevar, value_typevar],tuple[bool,str|None]]|None=None,
            value_function:Callable[[key_typevar, value_typevar],tuple[bool,str|None]]|None=None,
            additional_function:Callable[[Mapping[key_typevar, value_typevar]],tuple[bool,str|None]]|None=None,
            type_check:bool=True,
        ) -> None:
        if TYPE_CHECK_TYPE_VERIFIERS and type_check:
            private__dict_type_verifier.base_verify({
                "data_type": data_type,
                "key_type": key_type,
                "value_type": value_type,
                "data_type_str": data_type_str,
                "key_type_str": key_type_str,
                "value_type_str": value_type_str,
                "key_function": key_function,
                "value_function": value_function,
                "additional_function": additional_function,
            }, ["DictTypeVerifier"])
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

    def verify(self, data: Mapping[key_typevar, value_typevar], trace:Trace) -> list[Exceptions.TypeVerificationTypeException]:
        exceptions:list[Exceptions.TypeVerificationTypeException] = []
        if not isinstance(data, self.data_type):
            exceptions.append(Exceptions.TypeVerificationTypeError(trace, self.data_type_str, type(data)))
            return exceptions
        for index, (key, value) in enumerate(data.items()):
            if self.key_type_is_verifier:
                new_exceptions = cast(TypeVerifier, self.key_type).verify(key, trace.copy(key, TraceItemType.KEY))
                if len(new_exceptions) > 0:
                    exceptions.extend(new_exceptions)
                    continue
            else:
                if not isinstance(key, self.key_type): # type: ignore
                    exceptions.append(Exceptions.TypeVerificationTypeError(trace.copy(index, TraceItemType.ITEM), self.key_type_str, type(key)))
                    continue
            if self.value_type_is_verifier:
                new_exceptions = cast(TypeVerifier, self.value_type).verify(value, trace.copy(key, TraceItemType.VALUE))
                if len(new_exceptions) > 0:
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
        if len(exceptions) > 0:
            return exceptions
        if self.additional_function is not None:
            additional_function_success, additional_function_message = self.additional_function(data)
            if not additional_function_success:
                exceptions.append(Exceptions.TypeVerificationFunctionError(trace, additional_function_message, data))
        return exceptions

    def __repr__(self) -> str:
        return "<%s \"%s\", \"%s\", \"%s\">" % (self.__class__.__name__, self.key_type_str, self.value_type_str, self.data_type_str)

class TypedDictKeyTypeVerifier(TypeVerifier[tuple[key_typevar, value_typevar]]):

    def __init__(
            self,
            key:key_typevar,
            value_str:str,
            required:bool,
            value_type:type[value_typevar]|tuple[type[value_typevar],...]|TypeVerifier[value_typevar],
            function:Callable[[key_typevar, value_typevar],tuple[bool,str|None]]|None=None,
            type_check:bool=True,
        ) -> None:
        if TYPE_CHECK_TYPE_VERIFIERS and type_check:
            private__typed_dict_key_type_verifier.base_verify({
                "key": key,
                "value_str": value_str,
                "required": required,
                "value_type": value_type,
                "function": function,
            }, ["TypedDictKeyTypeVerifier"])
        self.key = key
        self.value_type = value_type
        self.value_type_is_verifier = isinstance(value_type, TypeVerifier)
        self.value_type_str = value_str
        self.required = required
        self.function = function

    def verify(self, data:tuple[key_typevar, value_typevar], trace:Trace) -> list[Exceptions.TypeVerificationTypeException]:
        exceptions:list[Exceptions.TypeVerificationTypeException] = []
        key, value = data
        if self.value_type_is_verifier:
            new_exceptions = cast(TypeVerifier, self.value_type).verify(value, trace.copy(key, TraceItemType.VALUE))
            if len(new_exceptions) > 0:
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
        return "<%s %s \"%s\">" % (self.__class__.__name__, self.key, self.value_type_str)

class TypedDictTypeVerifier(TypeVerifier[Mapping[Any, Any]]):

    def __init__(
            self,
            *keys:TypedDictKeyTypeVerifier,
            data_type:type[Mapping]|tuple[type[Mapping],...]=dict,
            data_type_str:str="a dict",
            function:Callable[[Mapping[key_typevar, value_typevar]],tuple[bool,str|None]]|None=None,
            loose:bool=False,
            type_check:bool=True,
        ) -> None:
        if TYPE_CHECK_TYPE_VERIFIERS and type_check:
            private__typed_dict_type_verifier.base_verify({
                "keys": keys,
                "data_type": data_type,
                "data_type_str": data_type_str,
                "function": function,
                "loose": loose,
            }, ["TypedDictTypeVerifier"])
        self.keys_dict = {key.key: key for key in keys}
        self.data_type = data_type
        self.data_type_str = data_type_str
        self.function = function
        self.loose = loose

        self.required_keys = [key.key for key in keys if key.required]

    def verify(self, data: Mapping[Any, Any], trace:Trace) -> list[Exceptions.TypeVerificationTypeException]:
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
            if len(new_exceptions) > 0:
                exceptions.extend(new_exceptions)
                continue
        for required_key in self.required_keys:
            if required_key not in data:
                exceptions.append(Exceptions.TypeVerificationMissingKeyError(trace.copy(required_key, TraceItemType.KEY)))
                continue
        if len(exceptions) > 0:
            return exceptions
        if self.function is not None:
            function_success, function_message = self.function(data)
            if not function_success:
                exceptions.append(Exceptions.TypeVerificationFunctionError(trace, function_message, data))
        return exceptions

    def __repr__(self) -> str:
        return "<%s \"%s\" (%s)>" % (self.__class__.__name__, self.data_type_str, ", ".join(self.keys_dict))

class ListTypeVerifier(TypeVerifier[Sequence[item_typevar]]):

    def __init__(
            self,
            item_type:type[item_typevar]|tuple[type[item_typevar],...]|TypeVerifier[item_typevar],
            data_type:type[Sequence]|tuple[type[Sequence],...],
            item_type_str:str,
            data_type_str:str,
            item_function:Callable[[item_typevar],tuple[bool,str|None]]|None=None,
            additional_function:Callable[[Sequence[item_typevar]],tuple[bool,str|None]]|None=None,
            type_check:bool=True,
        ) -> None:
        if TYPE_CHECK_TYPE_VERIFIERS and type_check:
            private__list_type_verifier.base_verify({
                "item_type": item_type,
                "data_type": data_type,
                "item_type_str": item_type_str,
                "data_type_str": data_type_str,
                "item_function": item_function,
                "additional_function": additional_function,
            }, ["ListTypeVerifier"])
        self.item_type = item_type
        self.item_type_is_verifier = isinstance(item_type, TypeVerifier)
        self.data_type = data_type
        self.item_type_str = item_type_str
        self.data_type_str = data_type_str
        self.item_function = item_function
        self.additional_function = additional_function

    def verify(self, data: Sequence[item_typevar], trace:Trace) -> list[Exceptions.TypeVerificationTypeException]:
        exceptions:list[Exceptions.TypeVerificationTypeException] = []
        if not isinstance(data, self.data_type):
            exceptions.append(Exceptions.TypeVerificationTypeError(trace, self.data_type_str, type(data)))
            return exceptions
        for index, item in enumerate(data):
            if self.item_type_is_verifier:
                new_exceptions = cast(TypeVerifier, self.item_type).verify(item, trace.copy(index, TraceItemType.ITEM))
                if len(new_exceptions) > 0:
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
        if len(exceptions) > 0:
            return exceptions
        if self.additional_function is not None:
            additional_function_success, additional_function_message = self.additional_function(data)
            if not additional_function_success:
                exceptions.append(Exceptions.TypeVerificationFunctionError(trace, additional_function_message, data))
        return exceptions

    def __repr__(self) -> str:
        return "<%s \"%s\" \"%s\">" % (self.__class__.__name__, self.item_type_str, self.data_type_str)

class IterableTypeVerifier(ListTypeVerifier):

    def __init__(
            self,
            item_type:type[item_typevar]|tuple[type[item_typevar],...]|TypeVerifier[item_typevar],
            data_type:type[Iterable]|tuple[type[Iterable],...],
            item_type_str:str,
            data_type_str:str,
            item_function:Callable[[item_typevar],tuple[bool,str|None]]|None=None,
            additional_function:Callable[[Iterable[item_typevar]],tuple[bool,str|None]]|None=None,
            type_check:bool=True,
        ) -> None:
        return super().__init__(item_type, cast(type[Sequence]|tuple[type[Sequence],...], data_type), item_type_str, data_type_str, item_function, additional_function, type_check)

    def verify(self, data: Iterable[item_typevar], trace:Trace) -> list[Exceptions.TypeVerificationTypeException]:
        return super().verify(cast(Sequence[item_typevar], data), trace)

class TupleItemTypeVerifier(TypeVerifier[tuple[int,item_typevar]]):
    def __init__(
            self,
            item_type:type[item_typevar]|tuple[type[item_typevar],...]|TypeVerifier[item_typevar],
            item_type_str:str,
            type_check:bool=True,
        ) -> None:
        if TYPE_CHECK_TYPE_VERIFIERS and type_check:
            private__tuple_item_type_verifier.base_verify({
                "item_type": item_type,
                "item_type_str": item_type_str,
            }, ["TupleItemTypeVerifier"])
        self.item_type = item_type
        self.item_type_is_verifier = isinstance(item_type, TypeVerifier)
        self.item_type_str = item_type_str

    def verify(self, data: tuple[int, item_typevar], trace:Trace) -> list[Exceptions.TypeVerificationTypeException]:
        index, item = data
        exceptions:list[Exceptions.TypeVerificationTypeException] = []
        if self.item_type_is_verifier:
            exceptions.extend(cast(TypeVerifier, self.item_type).verify(item, trace.copy(index, TraceItemType.ITEM)))
        else:
            if not isinstance(item, self.item_type): # type: ignore
                exceptions.append(Exceptions.TypeVerificationTypeError(trace.copy(index, TraceItemType.ITEM), self.item_type_str, type(item)))
        return exceptions

    def __repr__(self) -> str:
        return "<%s \"%s\">" % (self.__class__.__name__, self.item_type_str)

class TupleTypeVerifier(TypeVerifier[Sequence[item_typevar]]):

    def __init__(
            self,
            *items:TupleItemTypeVerifier[Any],
            data_type:type[Sequence]|tuple[type[Sequence],...]=tuple,
            data_type_str:str="a tuple",
            function:Callable[[Sequence[item_typevar]],tuple[bool,str|None]]|None=None,
            type_check:bool=True,
        ) -> None:
        if TYPE_CHECK_TYPE_VERIFIERS and type_check:
            private__tuple_type_verifier.base_verify({
                "data_type": data_type,
                "data_type_str": data_type_str,
                "items": items,
                "function": function
            }, ["TupleTypeVerifier"])
        self.items = items
        self.data_type = data_type
        self.data_type_str = data_type_str
        self.function = function

    def verify(self, data: Sequence[item_typevar], trace:Trace) -> list[Exceptions.TypeVerificationTypeException]:
        exceptions:list[Exceptions.TypeVerificationTypeException] = []
        if not isinstance(data, self.data_type):
            exceptions.append(Exceptions.TypeVerificationTypeError(trace, self.data_type_str, type(data)))
            return exceptions
        if len(data) != len(self.items):
            exceptions.append(Exceptions.TypeVerificationWrongLengthError(trace, len(self.items), len(data)))
            return exceptions
        for index, (item, type_verifier) in enumerate(zip(data, self.items)):
            new_exceptions = type_verifier.verify((index, item), trace)
            if len(new_exceptions) > 0:
                exceptions.extend(new_exceptions)
                continue
        if len(exceptions) > 0:
            return exceptions
        if self.function is not None:
            function_success, function_message = self.function(data)
            if not function_success:
                exceptions.append(Exceptions.TypeVerificationFunctionError(trace, function_message, data))
        return exceptions

    def __repr__(self) -> str:
        return "<%s \"%s\" len %i>" % (self.__class__.__name__, self.data_type_str, len(self.items))

class EnumTypeVerifier(TypeVerifier[item_typevar]):

    def __init__(self, options:Container, type_check:bool=True) -> None:
        if TYPE_CHECK_TYPE_VERIFIERS and type_check:
            private__enum_type_verifier.base_verify({"options": options}, ["EnumTypeVerifier"])
        self.options = options

    def verify(self, data: item_typevar, trace:Trace) -> list[Exceptions.TypeVerificationTypeException]:
        exceptions:list[Exceptions.TypeVerificationTypeException] = []
        if data not in self.options:
            exceptions.append(Exceptions.TypeVerificationEnumError(trace, self.options, data))
        return exceptions

    def __repr__(self) -> str:
        return "<%s %r>" % (self.__class__.__name__, self.options)

class UnionTypeVerifier(TypeVerifier[item_typevar]):

    def __init__(self, type_str:str, *types:type[item_typevar]|TypeVerifier[item_typevar]|Any, type_check:bool=True) -> None:
        if TYPE_CHECK_TYPE_VERIFIERS and type_check:
            private__union_type_verifier.base_verify({
                "type_str": type_str,
                "types": types,
            }, ["UnionTypeVerifier"])
        self.types = types
        self.types_are_type_verifiers = [isinstance(type, TypeVerifier) for type in types]
        self.type_str = type_str

    def verify(self, data: item_typevar, trace: Trace) -> list[Exceptions.TypeVerificationTypeException]:
        exceptions:list[Exceptions.TypeVerificationTypeException] = []
        union_exceptions:list[list[Exceptions.TypeVerificationTypeException]] = []
        for type_verifier, is_type_verifier in zip(self.types, self.types_are_type_verifiers):
            if is_type_verifier:
                new_exceptions = cast(TypeVerifier, type_verifier).verify(data, trace)
                if len(new_exceptions) == 0: return []
                else: union_exceptions.append(new_exceptions)
            else:
                if isinstance(data, type_verifier): # type: ignore
                    return []
        else:
            exceptions.append(Exceptions.TypeVerificationUnionError(trace, self.type_str, type(data), union_exceptions))
        return exceptions

    def __repr__(self) -> str:
        return "<%s \"%s\">" % (self.__class__.__name__, self.type_str)

NoneType = type(None)
special_type:type = type(Callable).mro()[2]|NoneType # type: ignore # you can't stop me, Python!
cannot_be_none_function = lambda data: (data is not None, "data cannot be None!")
cannot_be_none_key_function = lambda key, value: (value is not None, "value cannot be None!")

private__dict_type_verifier = TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("data_type", "a type or tuple", True, UnionTypeVerifier("a type or tuple of types", (type, special_type), ListTypeVerifier((type, special_type), tuple, "a type", "a tuple", item_function=cannot_be_none_function, type_check=False), type_check=False), function=cannot_be_none_key_function, type_check=False),
    TypedDictKeyTypeVerifier("key_type", "a type, tuple, or TypeVerifier", True, UnionTypeVerifier("a type, tuple of types, or TypeVerifier", (type, special_type), TypeVerifier, ListTypeVerifier((type, special_type), tuple, "a type", "a tuple", item_function=cannot_be_none_function, type_check=False), type_check=False), function=cannot_be_none_key_function, type_check=False),
    TypedDictKeyTypeVerifier("value_type", "a type, tuple, or TypeVerifier", True, UnionTypeVerifier("a type, tuple of types, or TypeVerifier", (type, special_type), TypeVerifier, ListTypeVerifier((type, special_type), tuple, "a type", "a tuple", item_function=cannot_be_none_function, type_check=False), type_check=False), function=cannot_be_none_key_function, type_check=False),
    TypedDictKeyTypeVerifier("data_type_str", "a str", True, str, type_check=False),
    TypedDictKeyTypeVerifier("key_type_str", "a str", True, str, type_check=False),
    TypedDictKeyTypeVerifier("value_type_str", "a str", True, str, type_check=False),
    TypedDictKeyTypeVerifier("key_function", "a Callable or None", True, (Callable, NoneType), type_check=False),
    TypedDictKeyTypeVerifier("value_function", "a Callable or None", True, (Callable, NoneType), type_check=False),
    TypedDictKeyTypeVerifier("additional_function", "a Callable or None", True, (Callable, NoneType), type_check=False),
    type_check=False,
)

private__typed_dict_key_type_verifier = TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("key", "an object", True, object, type_check=False),
    TypedDictKeyTypeVerifier("value_str", "a str", True, str, type_check=False),
    TypedDictKeyTypeVerifier("required", "a bool", True, bool, type_check=False),
    TypedDictKeyTypeVerifier("value_type", "a type, tuple, or TypeVerifier", True, UnionTypeVerifier("a type, tuple of types, or TypeVerifier", type, special_type, TypeVerifier, ListTypeVerifier((type, special_type), tuple, "a type", "a tuple", item_function=cannot_be_none_function, type_check=False), type_check=False), function=cannot_be_none_key_function, type_check=False),
    TypedDictKeyTypeVerifier("function", "a Callable or None", True, (Callable, NoneType), type_check=False),
    type_check=False,
)

private__typed_dict_type_verifier = TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("keys", "a tuple", True, ListTypeVerifier(TypedDictKeyTypeVerifier, tuple, "a TypedDictKeyTypeVerifier", "a tuple", type_check=False), type_check=False),
    TypedDictKeyTypeVerifier("data_type", "a type or tuple", True, UnionTypeVerifier("a type or tuple of types", type, special_type, ListTypeVerifier((type, special_type), tuple, "a type", "a tuple", item_function=cannot_be_none_function, type_check=False), type_check=False), function=cannot_be_none_key_function, type_check=False),
    TypedDictKeyTypeVerifier("data_type_str", "a str", True, str, type_check=False),
    TypedDictKeyTypeVerifier("function", "a Callable or None", True, (Callable, NoneType), type_check=False),
    TypedDictKeyTypeVerifier("loose", "a bool", True, bool),
    type_check=False,
)

private__list_type_verifier = TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("item_type", "a type, tuple, or TypeVerifier", True, UnionTypeVerifier("a type, tuple of types, or TypeVerifier", type, special_type, TypeVerifier, ListTypeVerifier((type, special_type), tuple, "a type", "a tuple", item_function=cannot_be_none_function, type_check=False), type_check=False), function=cannot_be_none_key_function, type_check=False),
    TypedDictKeyTypeVerifier("data_type", "a type or tuple", True, UnionTypeVerifier("a type or tuple of types", type, special_type, ListTypeVerifier((type, special_type), tuple, "a type", "a tuple", item_function=cannot_be_none_function, type_check=False), type_check=False), function=cannot_be_none_key_function, type_check=False),
    TypedDictKeyTypeVerifier("item_type_str", "a str", True, str, type_check=False),
    TypedDictKeyTypeVerifier("data_type_str", "a str", True, str, type_check=False),
    TypedDictKeyTypeVerifier("item_function", "a Callable or None", True, (Callable, NoneType), type_check=False),
    TypedDictKeyTypeVerifier("additional_function", "a Callable or None", True, (Callable, NoneType), type_check=False),
    type_check=False,
)

private__tuple_item_type_verifier = TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("item_type", "a type, tuple, or TypeVerifier", True, UnionTypeVerifier("a type, tuple of types, or TypeVerifier", type, special_type, TypeVerifier, ListTypeVerifier((type, special_type), tuple, "a type", "a tuple", item_function=cannot_be_none_function, type_check=False), type_check=False), function=cannot_be_none_key_function, type_check=False),
    TypedDictKeyTypeVerifier("item_type_str", "a str", True, str, type_check=False),
    type_check=False,
)

private__tuple_type_verifier = TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("data_type", "a type, tuple, or tuple", True, UnionTypeVerifier("a type, tuple of types, or TypeVerifier", type, special_type, TypeVerifier, ListTypeVerifier((type, special_type), tuple, "a type", "a tuple", item_function=cannot_be_none_function, type_check=False), type_check=False), function=cannot_be_none_key_function, type_check=False),
    TypedDictKeyTypeVerifier("data_type_str", "a str", True, str, type_check=False),
    TypedDictKeyTypeVerifier("items", "a tuple", True, ListTypeVerifier(TupleItemTypeVerifier, tuple, "a TupleItemTypeVerifier", "a tuple", type_check=False), type_check=False),
    TypedDictKeyTypeVerifier("function", "a Callable or None", True, (Callable, NoneType), type_check=False),
    type_check=False,
)

private__enum_type_verifier = TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("options", "a Container", True, Container, type_check=False),
    type_check=False
)

private__union_type_verifier = TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("type_str", "a str", True, str, type_check=False),
    TypedDictKeyTypeVerifier("types", "a tuple", True, ListTypeVerifier((type, special_type, TypeVerifier), tuple, "a type or TypeVerifier", "a tuple", item_function=cannot_be_none_function, type_check=False), type_check=False),
    type_check=False
)
