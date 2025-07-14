from typing import Any, Literal, NotRequired, Required, TypedDict

from Component.ComponentFunctions import component_function

# Only the type key and its corresponding identifying key are present.

class TextTypedDict(TypedDict):
    type: NotRequired[Literal["text"]]
    text: Required[str]

class TranslatableTypedDict(TypedDict):
    type: NotRequired[Literal["translatable"]]
    translate: Required[str]

class ScoreTypedDict(TypedDict):
    type: NotRequired[Literal["score"]]
    score: Required[dict[str,Any]]

class SelectorTypedDict(TypedDict):
    type: NotRequired[Literal["selector"]]
    selector: Required[str]

class KeybindTypedDict(TypedDict):
    type: NotRequired[Literal["keybind"]]
    keybind: Required[str]

class NbtTypedDict(TypedDict):
    type: NotRequired[Literal["nbt"]]
    nbt: Required[str]

type TextComponent = TextTypedDict|TranslatableTypedDict|ScoreTypedDict|SelectorTypedDict|KeybindTypedDict|NbtTypedDict

VALID_TYPES = {
    "text": "text",
    "translatable": "translate",
    "score": "score",
    "selector": "selector",
    "keybind": "keybind",
    "nbt": "nbt",
}

@component_function(no_arguments=True)
def text_component_choose(data:TextComponent|dict[str,Any]) -> str:
    type_value = data.get("type")
    if type_value in VALID_TYPES and VALID_TYPES[type_value] in data:
        return type_value
    # determine type automatically
    for type_value, required_key in VALID_TYPES.items():
        if required_key in data:
            return type_value
    else:
        return "ERROR" # no information is given on what to do in this circumstance.
