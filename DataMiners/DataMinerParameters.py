from typing import Any, Generator, Generic, TypeVar, Union

# I swear this is not comparer 2 electric boogaloo

ParametersDataType = TypeVar("ParametersDataType")

class Parameters(Generic[ParametersDataType]): # Abstract type

    accepted_type: type

    def check_type_or_parameter(self, data:Union["Parameters",type,tuple[type,...]], parameter_name:str) -> None:
        if not isinstance(data, (Parameters, type, tuple)):
            raise TypeError("%s is not a Parameters, type, or tuple, but instead %s!" % (parameter_name, data.__class__.__name__))
        if isinstance(data, tuple):
            for index, item in enumerate(data):
                if not isinstance(item, type):
                    raise TypeError("Item %i of `%s` is not a type, but instead %s!" % (index, parameter_name, item.__class__.__name__))

    def validate(self, data:ParametersDataType) -> Generator[Exception, None, None]:
        raise NotImplementedError()

class DictParameters(Parameters[dict[str,Any]]):

    accepted_type = dict

    def __init__(self, value_type:Parameters|type|tuple[type,...]) -> None:
        self.check_type_or_parameter(value_type, "`value_type`")
        self.value_type = value_type

    def validate(self, data) -> Generator[Exception, None, None]:
        for index, (key, value) in enumerate(data.items()):
            if not isinstance(key, str):
                yield TypeError("Key number %i is not a str, but instead \"%s\"!" % (index, key.__class__.__name__))
                continue
            match self.value_type:
                case Parameters():
                    if not isinstance(value, self.value_type.accepted_type):
                        yield TypeError("Value of key \"%s\" is not a %s, but instead %s!" % (key, self.value_type.accepted_type, value.__class__.__name__))
                        continue
                    yield from self.value_type.validate(value)
                case type() | tuple():
                    if not isinstance(value, self.value_type):
                        yield TypeError("Value of key \"%s\" is not a %s, but instead %s!" % (key, self.value_type, value.__class__.__name__))
                        continue

class ListParameters(Parameters[list[Any]]):

    accepted_type = list

    def __init__(self, item_type:Parameters|type|tuple[type,...]) -> None:
        self.check_type_or_parameter(item_type, "`item_type`")

        self.item_type = item_type
    
    def validate(self, data) -> Generator[Exception, None, None]:
        for index, item in enumerate(data):
            match self.item_type:
                case Parameters():
                    if not isinstance(item, self.item_type.accepted_type):
                        yield TypeError("Item %i is not a %s, but instead %s!" % (index, self.item_type, item.__class__.__name__))
                        continue
                    yield from self.item_type.validate(item)
                case type() | tuple():
                    if not isinstance(item, self.item_type):
                        yield TypeError("Item %i is not a %s, but instead %s!" % (index, self.item_type, item.__class__.__name__))
                        continue

class LiteralParameters(Parameters):

    accepted_type = object # Would rather get a more complete error message than just that the type is wrong

    def __init__(self, values:list[Any]|set[Any]) -> None:
        if not isinstance(values, (list, set)):
            raise TypeError("`values` is not a list or set, but instead %s!" % (values.__class__.__name__))
        
        self.values = values
    
    def validate(self, data: Any) -> Generator[Exception, None, None]:
        if data not in self.values:
            yield ValueError("Value is \"%s\" instead of one of %s!" % (data, self.values))

class TypedDictParameters(Parameters[dict[str,Any]]):

    accepted_type = dict

    def __init__(self, keys:dict[str,tuple[Parameters|type|tuple[type,...],bool]]) -> None:
        '''Give it a dict of keys and a Parameters object or a type object and a is_required boolean.'''
        if not isinstance(keys, dict):
            raise TypeError("`keys` is not a dict, but instead %s!" % keys.__class__.__name__)
        for index, (key, value) in enumerate(keys.items()):
            if not isinstance(key, str):
                raise TypeError("Key %i of `keys` is not a str, but instead %s!" % (index, key.__class__.__name__))
            if not isinstance(value, tuple):
                raise TypeError("Value of key \"%s\" of `keys` is not a tuple, but instead %s!" % (key, value.__class__.__name__))
            if len(value) != 2:
                raise ValueError("Value of key \"%s\" is not length 2, but instead %i!" % (key, len(value)))
            value_type, is_required = value
            self.check_type_or_parameter(value_type, "Item 1 of value of key \"%s\" of `keys`" % (key))
            if not isinstance(is_required, bool):
                raise TypeError("Item 2 of value of key \"%s\" is not a bool, but instead %s!" % (key, is_required.__class__.__name__))

        self.keys = {key: value[0] for key, value in keys.items()}
        self.required_keys = [key for key, value in keys.items() if value is True]

    def validate(self, data) -> Generator[Exception, None, None]:
        for required_key in self.required_keys:
            if required_key not in data:
                yield KeyError("Required key \"%s\" does not exist!" % required_key)
                continue
        for index, (key, value) in enumerate(data.items()):
            if not isinstance(key, str):
                yield TypeError("Key number %i is not a str, but instead \"%s\"!" % (index, key.__class__.__name__))
                continue
            if key not in self.keys:
                yield KeyError("Key \"%s\" is not a valid key!" % (key))
                continue
            value_type = self.keys[key]
            match value_type:
                case Parameters():
                    if not isinstance(value, value_type.accepted_type):
                        yield TypeError("Value of key \"%s\" is not a %s, but instead %s!" % (key, value_type.accepted_type, value.__class__.__name__))
                        continue
                    yield from value_type.validate(value)
                case type() | tuple():
                    if not isinstance(value, value_type):
                        yield TypeError("Value of key \"%s\" is not a %s, but instead %s!" % (key, value_type, value.__class__.__name__))
                        continue
