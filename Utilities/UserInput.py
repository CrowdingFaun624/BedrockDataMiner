from itertools import chain
from types import EllipsisType
from typing import Callable, Iterable, Mapping, NoReturn


def get_levenshtein_distance(data1:str, data2:str) -> int:
    distances:list[list[int]] = [[0] * (len(data1) + 1) for y in range(len(data2) + 1)]
    for x in range(1, len(data1) + 1):
        distances[0][x] = x
    for y in range(1, len(data2) + 1):
        distances[y][0] = y
    for y in range(len(data2)):
        for x in range(len(data1)):
            distances[y + 1][x + 1] = min(
                distances[y+1][x] + 2,
                distances[y][x+1] + 2,
                distances[y][x] + (0 if data1[x] == data2[y] else (1 if data1[x].lower() == data2[y].lower() else 2)),
            )
    distance = distances[len(data2)][len(data1)]
    return distance

def guess_intent(user_input:str, items:list[str], threshold:int) -> str|None:
    """
    Returns what the user probably wants based on their input, or returns None
    if it cannot be guessed.
    """
    if len(user_input) < 2: return None
    similarities:dict[str,int] = {option: get_levenshtein_distance(user_input, option) for option in items}
    min_option, min_distance, second_min_distance = None, None, None
    for option, distance in similarities.items():
        if distance > threshold * 2: continue # distances are multiplied by two, so threshold is too.
        if min_distance is None or distance <= min_distance:
            min_option = option
            second_min_distance = min_distance
            min_distance = distance
    if min_distance is not None and second_min_distance is not None and second_min_distance <= min_distance - 0:
        return None
    return min_option

def deduplicate_aliases[a](aliases:Mapping[str,Iterable[str]], items:Mapping[str,a]) -> Mapping[str,a]:
    aliases2 = {target: list(shortcuts) for target, shortcuts in aliases.items()}
    already_aliases:set[str] = set()
    duplicate_aliases:set[str] = set()
    for alias in chain.from_iterable(aliases2.values()):
        (duplicate_aliases if alias in already_aliases or alias in items else already_aliases).add(alias)
    aliases3:dict[str,list[str]] = {target: [shortcut for shortcut in shortcuts if shortcut not in duplicate_aliases] for target, shortcuts in aliases2.items()}
    output = {shortcut: items[target] for target, shortcuts in aliases3.items() for shortcut in shortcuts}
    output.update(items)
    return output

def default_prompt_single(label:str, options:list[str]|None) -> str:
    if options is None:
        return f"Choose a {label}: "
    else:
        return f"Choose a {label} ({", ".join(options)}): "

def default_prompt_multi(label:str, options:list[str]|None) -> str:
    if options is None:
        return f"Choose a/some {label} (space-delimited): "
    else:
        return f"Choose a/some {label} (space-delimited) ({", ".join(options)}): "

def input_single[a](
    items:Mapping[str,a],
    label:str,
    *,
    show_options:bool=False,
    show_options_first_time:bool=False,
    close_enough:bool=False,
    close_enough_threshold:int=3,
    prompt_function:Callable[[str, list[str]|None],str]=default_prompt_single,
    behavior_on_eof:Callable[[],NoReturn]|None=None,
    aliases:Mapping[str,Iterable[str]]|None=None,
    enter_can_pick_only:bool=False
) -> a:
    """
    Returns one item from `items`.

    By default, uses the prompt "Choose a &lt;label&gt;: "

    :param items: The items the user can choose from.
    :param label: The simple label to be given to the prompt function.
    :param show_options: If True, prints out all options by giving the options to the prompt function.
    :param show_options_first_time: If True, prints out all options if this is the user's first try.
    :param close_enough: If True, will attempt to guess the user's intent.
    :param close_enough_threshold: The maximum distance the guesses can have.
    :param prompt_function: Can be overridden to create a custom prompt.
    :param behavior_on_eof: Function that is called when input() raises an EOFError.
    :param aliases: Hidden shortcuts to another action.
    :param enter_can_pick_only: If True, entering no input will pick the only option if there is only one option.
    """
    user_input:str|EllipsisType = ...
    options:list[str] = list(items.keys())
    items = deduplicate_aliases({} if aliases is None else aliases, items)
    all_options:list[str] = list(items.keys())
    tries:int = 0
    while user_input not in items:
        should_show_options = tries == 0 and show_options_first_time or show_options
        try:
            user_input = input(prompt_function(label, options if should_show_options else None))
        except EOFError:
            if behavior_on_eof is None:
                raise
            else:
                behavior_on_eof()
        tries += 1
        if enter_can_pick_only and user_input == "" and len(items) == 1:
            return next(iter(items.values()))
        if close_enough and user_input not in items:
            user_guess = guess_intent(user_input, all_options, close_enough_threshold)
            if user_guess is not None:
                user_input = user_guess
                print(f"Assuming user means \"{user_guess}\"")
    assert user_input is not ... # Not sure why this is necessary all of a sudden.
    return items[user_input]

def input_multi[a](
    items:Mapping[str,a],
    label:str,
    *,
    allow_select_all:bool=True,
    show_options:bool=False,
    show_options_first_time:bool=False,
    close_enough:bool=False,
    close_enough_threshold:int=3,
    prompt_function:Callable[[str, list[str]|None],str]=default_prompt_multi,
    aliases:Mapping[str,Iterable[str]]|None=None,
    alternative_selectors:Mapping[str,Callable[[],list[str]]]|None=None,
    behavior_on_eof:Callable[[],NoReturn]|None=None,
) -> list[a]:
    """
    Returns one or multiple items from `items`.

    By default, uses the prompt "Choose a/some &lt;label&gt; (space-delimited): "

    :param items: The items the user can choose from.
    :param label: The simple label to be given to the prompt function.
    :param allow_select_all: If True, the user can type an asterisk and get all items.
    :param show_options: If True, prints out all options by giving the options to the prompt function.
    :param show_options_first_time: If True, prints out all options if this is the user's first try.
    :param close_enough: If True, will attempt to guess the user's intent.
    :param close_enough_threshold: The maximum distance the guesses can have.
    :param prompt_function: Can be overridden to create a custom prompt.
    :param aliases: Hidden shortcuts to another action.
    :param alternative_selectors: A dictionary of single-character strings that maps to a function that returns options.
    :param behavior_on_eof: Function that is called when input() raises an EOFError.
    """
    user_inputs:list[str] = []
    options:list[str] = list(items.keys())
    items = deduplicate_aliases({} if aliases is None else aliases, items)
    all_options = list(items.keys())
    tries:int = 0
    successful_inputs:list[str] = []
    successful_set:set[str] = set()
    should_retry:bool = True
    while should_retry:
        should_show_options:bool = tries == 0 and show_options_first_time or show_options
        try:
            user_input:str = input(prompt_function(label, options if should_show_options else None))
        except EOFError:
            if behavior_on_eof is None:
                raise
            else:
                behavior_on_eof()
        user_inputs:list[str] = user_input.split(" ")
        tries += 1
        if user_input == "" and len(successful_inputs) > 0:
            print("Returning...")
            break
        if allow_select_all and user_input == "*":
            user_inputs = options.copy()
        elif alternative_selectors is not None and user_input in alternative_selectors:
            user_inputs = alternative_selectors[user_input]()
        pop_indices:list[int] = []
        for index, item in enumerate(user_inputs):
            if item in items:
                if item not in successful_set:
                    successful_inputs.append(item)
                    successful_set.add(item)
                pop_indices.append(index)
        for index in reversed(pop_indices):
            user_inputs.pop(index)
        if len(user_inputs) > 0 and len(successful_inputs) > 0:
            print(f"Recognize {", ".join(successful_inputs)} so far.")
        if close_enough and len(user_inputs) > 0:
            pop_indices:list[int] = []
            guessed_items:list[tuple[str,str]] = []
            for index, item in enumerate(user_inputs):
                user_guess = guess_intent(item, all_options, close_enough_threshold)
                if user_guess is not None:
                    pop_indices.append(index)
                    guessed_items.append((item, user_guess))
                    successful_inputs.append(user_guess)
                    successful_set.add(user_guess)
            for index in reversed(pop_indices):
                user_inputs.pop(index)
            if len(guessed_items) > 0:
                print(f"Assuming {", ".join(f"\"{user_input}\" means \"{guess}\"" for user_input, guess in guessed_items)}.")
        should_retry = len(user_inputs) > 0
        if len(user_inputs) > 0:
            print(f"Cannot recognize {user_inputs}.")
    return [items[item] for item in successful_inputs]

def input_integer(
    label:str,
    *,
    may_be_negative:bool=True,
    may_be_zero:bool=True,
    prompt_function:Callable[[str, list[str]|None],str]=default_prompt_single,
    behavior_on_eof:Callable[[],NoReturn]|None=None,
) -> int:
    """
    Returns an integer.

    By default, uses the prompt "Choose a &lt;label&gt;: "

    :param label: The simple label to be given to the prompt function.
    :param may_be_negative: If True, negative inputs are allowed.
    :param may_be_zero: If True, an input of 0 is allowed.
    :param prompt_function: Can be overridden to create a custom prompt.
    :param behavior_on_eof: Function that is called when input() raises an EOFError.
    """
    while True:
        try:
            user_input:str = input(prompt_function(label, None))
        except EOFError:
            if behavior_on_eof is None:
                raise
            else:
                behavior_on_eof()
        try:
            user_integer = int(user_input)
        except ValueError:
            continue
        if not may_be_negative and user_integer < 0:
            print("Integer may not be negative!")
            continue
        if not may_be_zero and user_integer == 0:
            print("Integer may not be 0!")
            continue
        break
    return user_integer
