from typing import Any, NotRequired, Required, TypedDict

from Serializer.JsonSerializer import JsonSerializer
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    TypeVerifier,
)


class Condition():

    __slots__ = ()
    name:str
    type_verifier:TypeVerifier = TypedDictTypeVerifier()

    # stupid freaking linter won't accept it when it's dict[str,Any], dict[Any,Any], or TypedDict.
    def __init__(self, data:Any, trace:list[Any]|None=None) -> None:
        self.type_verifier.verify_throw(data, tuple(trace) if trace is not None else ())

    def match(self, data:bytes, is_exception:bool) -> bool: ...

    def has_exception_condition(self) -> bool:
        return False

class AlwaysCondition(Condition):

    __slots__ = ()
    name = "always"

    def match(self, data: bytes, is_exception:bool) -> bool:
        return True

class ExceptionCondition(Condition):

    __slots__ = ()
    name = "exception"

    def match(self, data: bytes, is_exception: bool) -> bool:
        return is_exception

    def has_exception_condition(self) -> bool:
        return True

class ContentConditionTypedDict(TypedDict):
    content: Required[str]

class ContentCondition(Condition):

    __slots__ = (
        "content",
    )

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("content", True, str),
    )

    def __init__(self, data: ContentConditionTypedDict, trace:list[Any]|None=None) -> None:
        super().__init__(data, trace)
        self.content = data["content"].encode()

class MatchCondition(ContentCondition):

    __slots__ = ()
    name = "match"

    def match(self, data: bytes, is_exception:bool) -> bool:
        return data == self.content

class SuffixCondition(ContentCondition):

    __slots__ = ()
    name = "suffix"

    def match(self, data: bytes, is_exception:bool) -> bool:
        return data.endswith(self.content)

class PrefixCondition(ContentCondition):

    __slots__ = ()
    name = "prefix"

    def match(self, data: bytes, is_exception:bool) -> bool:
        return data.startswith(self.content)

class MetaConditionTypedDict(TypedDict):
    conditions: Required[list[dict]]

class MetaCondition(Condition):

    __slots__ = (
        "conditions",
    )

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("conditions", True, ListTypeVerifier(dict, list))
    )

    def __init__(self, data: MetaConditionTypedDict, trace:list[Any]|None=None) -> None:
        super().__init__(data, trace)
        if trace is None: trace = []
        self.conditions = [parse_condition(condition, trace + ["conditions", index]) for index, condition in enumerate(data["conditions"])]

    def has_exception_condition(self) -> bool:
        return any(condition.has_exception_condition() for condition in self.conditions)

class AndCondition(MetaCondition):

    __slots__ = ()
    name = "and"

    def match(self, data: bytes, is_exception:bool) -> bool:
        return all(condition.match(data, is_exception) for condition in self.conditions)

class OrCondition(MetaCondition):

    __slots__ = ()
    name = "or"

    def match(self, data:bytes, is_exception:bool) -> bool:
        return any(condition.match(data, is_exception) for condition in self.conditions)

condition_types_list:list[type[Condition]] = [
    AlwaysCondition,
    AndCondition,
    ExceptionCondition,
    MatchCondition,
    OrCondition,
    PrefixCondition,
    SuffixCondition,
]

condition_types:dict[str,type[Condition]] = {condition_type.name: condition_type for condition_type in condition_types_list}

def parse_condition(data:dict[Any,Any], trace:list[Any]|None=None) -> Condition:
    condition_type_str:str = data.pop("type", "always")
    return condition_types[condition_type_str](data, trace)

class Action():

    __slots__ = ()
    name:str
    type_verifier:TypeVerifier = TypedDictTypeVerifier()

    def __init__(self, data:Any, trace:list[Any]|None=None) -> None:
        self.type_verifier.verify_throw(data, tuple(trace) if trace is not None else ())

    def do(self, data:bytes) -> bytes: ...

class ContentActionTypedDict(TypedDict):
    content: Required[str]

class ContentAction(Action):

    __slots__ = (
        "content",
    )

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("content", True, str),
    )

    def __init__(self, data: ContentActionTypedDict, trace: list[Any] | None = None) -> None:
        super().__init__(data, trace)
        self.content = data["content"].encode()

class ReplaceAction(ContentAction):

    __slots__ = ()
    name = "replace"

    def do(self, data: bytes) -> bytes:
        return self.content

class AppendAction(ContentAction):

    __slots__ = ()
    name = "append"

    def do(self, data:bytes) -> bytes:
        return data + self.content

class PrependAction(ContentAction):

    __slots__ = ()
    name = "prepend"

    def do(self, data: bytes) -> bytes:
        return self.content + data

class RemoveSuffixAction(ContentAction):

    __slots__ = ()
    name = "remove_suffix"

    def do(self, data: bytes) -> bytes:
        return data.removesuffix(self.content)

class RemovePrefixAction(ContentAction):

    __slots__ = ()
    name = "remove_prefix"

    def do(self, data: bytes) -> bytes:
        return data.removeprefix(self.content)

class ReplaceSomeActionTypedDict(TypedDict):
    count: NotRequired[int]
    old_content: Required[str]
    new_content: Required[str]

class ReplaceSomeAction(Action):

    __slots__ = (
        "count",
        "new_content",
        "old_content",
    )

    name = "replace_some"
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("count", False, int),
        TypedDictKeyTypeVerifier("new_content", True, str),
        TypedDictKeyTypeVerifier("old_content", True, str),
    )

    def __init__(self, data: ReplaceSomeActionTypedDict, trace: list[Any] | None = None) -> None:
        super().__init__(data, trace)
        self.old_content = data["old_content"].encode()
        self.new_content = data["new_content"].encode()
        self.count = data.get("count", -1)

    def do(self, data: bytes) -> bytes:
        return data.replace(self.old_content, self.new_content, self.count)

class SequenceActionTypedDict(TypedDict):
    actions: Required[list[dict]]

class SequenceAction(Action):

    __slots__ = (
        "actions",
    )

    name = "sequence"
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("actions", True, ListTypeVerifier(dict, list)),
    )

    def __init__(self, data: Any, trace: list[Any] | None = None) -> None:
        super().__init__(data, trace)
        if trace is None:
            trace = []
        self.actions = [parse_action(action, trace + ["actions", index]) for index, action in enumerate(data["actions"])]

    def do(self, data: bytes) -> bytes:
        for action in self.actions:
            data = action.do(data)
        return data

action_types_list:list[type[Action]] = [
    AppendAction,
    PrependAction,
    RemovePrefixAction,
    RemoveSuffixAction,
    ReplaceAction,
    ReplaceSomeAction,
    SequenceAction,
]
action_types:dict[str,type[Action]] = {action.name: action for action in action_types_list}

def parse_action(action:dict[Any,Any], trace:list[Any]|None=None) -> Action:
    action_type_str = action.pop("type")
    return action_types[action_type_str](action, trace)

class RulesTypedDict(TypedDict):
    condition: dict[Any,Any]
    action: dict[Any,Any]

class Rule():

    __slots__ = (
        "action",
        "condition",
        "index",
        "serializer_name",
    )

    def __init__(self, serializer_name:str, index:int, condition:Condition, action:Action) -> None:
        self.serializer_name = serializer_name
        self.index = index
        self.condition = condition
        self.action = action

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.index} of {self.serializer_name}>"

    def do(self, data:bytes, is_exception:bool) -> tuple[bool, bytes]:
        if self.condition.match(data, is_exception):
            return True, self.action.do(data)
        else:
            return False, data

    def has_exception_condition(self) -> bool:
        return self.condition.has_exception_condition()

class RepairableJsonSerializer(JsonSerializer):

    __slots__ = (
        "empty_okay",
        "rules",
    )

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("empty_okay", False, bool),
        TypedDictKeyTypeVerifier("rules", True, ListTypeVerifier(TypedDictTypeVerifier(
            TypedDictKeyTypeVerifier("condition", True, dict),
            TypedDictKeyTypeVerifier("action", True, dict)
        ), list))
    )

    def initialize(self, rules:list[RulesTypedDict], empty_okay:bool=False) -> None:
        self.rules = [Rule(self.full_name, index, parse_condition(rule["condition"]), parse_action(rule["action"])) for index, rule in enumerate(rules)]
        self.empty_okay = empty_okay

    def do_rules(self, data:bytes, is_exception:bool) -> tuple[bool,bytes]:
        did_anything = False
        for rule in self.rules:
            did_something, data = rule.do(data, is_exception)
            did_anything = did_anything or did_something
        return did_anything, data

    def deserialize(self, data: bytes) -> Any:
        _, processed_data = self.do_rules(data, False)
        try:
            return super().deserialize(processed_data)
        except Exception:
            did_anything, processed_data2 = self.do_rules(processed_data, True)
            if not did_anything:
                raise
            return super().deserialize(processed_data2)
