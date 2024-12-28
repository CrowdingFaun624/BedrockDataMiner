from types import EllipsisType
from typing import Callable, NoReturn


def get_levenshtein_distance(data1:str, data2:str) -> int:
    distances:list[list[int]] = [[0] * (len(data1) + 1) for y in range(len(data2) + 1)]
    for x in range(1, len(data1) + 1):
        distances[0][x] = x
    for y in range(1, len(data2) + 1):
        distances[y][0] = y
    for y in range(len(data2)):
        for x in range(len(data1)):
            distances[y + 1][x + 1] = min(
                distances[y+1][x] + 1,
                distances[y][x+1] + 1,
                distances[y][x] + int(data1[x] != data2[y]),
            )
    distance = distances[len(data2)][len(data1)]
    return distance
    # return 1 - (distance / max(len(data1), len(data2)))

def guess_intent(user_input:str, options:list[str], threshold:int) -> str|None:
    '''
    Returns what the user probably wants based on their input, or returns None
    if it cannot be guessed.
    '''
    similarities:dict[str,int] = {option: get_levenshtein_distance(user_input, option) for option in options}
    min_option, min_distance = None, None
    for option, distance in similarities.items():
        if distance > threshold: continue
        if min_distance is None or distance < min_distance:
            min_option = option
            min_distance = distance
    return min_option

def default_prompt_single(label:str, options:list[str]|None) -> str:
    if options is None:
        return "Choose a %s: " % (label,)
    else:
        return "Choose a %s (%s): " % (label, ", ".join(options))

def default_prompt_multi(label:str, options:list[str]|None) -> str:
    if options is None:
        return "Choose a/some %s (space-delimited): " % (label,)
    else:
        return "Choose a/some %s (space-delimited) (%s): " % (label, ", ".join(options))

def input_single[a](
    items:dict[str,a],
    label:str,
    *,
    show_options:bool=False,
    show_options_first_time:bool=False,
    close_enough:bool=False,
    close_enough_threshold:int=3,
    prompt_function:Callable[[str, list[str]|None],str]=default_prompt_single,
    behavior_on_eof:Callable[[],NoReturn]|None=None,
) -> a:
    '''
    Returns one item from `items`.

    By default, uses the prompt "Choose a \\<label\\>: "

    :items: The items the user can choose from.
    :label: The simple label to be given to the prompt function.
    :show_options: If True, prints out all options by giving the options to the prompt function.
    :show_options_first_time: If True, prints out all options if this is the user's first try.
    :close_enough: If True, will attempt to guess the user's intent.
    :close_enough_threshold: The maximum distance the guesses can have.
    :prompt_function: Can be overridden to create a custom prompt.
    :behavior_on_eof: Function that is called when input() raises an EOFError.
    '''
    user_input:str|EllipsisType = ...
    options:list[str] = list(items.keys())
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
        if close_enough and user_input not in items:
            user_guess = guess_intent(user_input, options, close_enough_threshold)
            if user_guess is not None:
                user_input = user_guess
                print("Assuming user means \"%s\"" % (user_guess,))
    return items[user_input]

def input_multi[a](
    items:dict[str,a],
    label:str,
    *,
    allow_select_all:bool=True,
    show_options:bool=False,
    show_options_first_time:bool=False,
    close_enough:bool=False,
    close_enough_threshold:int=3,
    prompt_function:Callable[[str, list[str]|None],str]=default_prompt_multi,
    behavior_on_eof:Callable[[],NoReturn]|None=None,
) -> list[a]:
    '''
    Returns one or multiple items from `items`.

    By default, uses the prompt "Choose a/some \\<label\\> (space-delimited): "

    :items: The items the user can choose from.
    :label: The simple label to be given to the prompt function.
    :allow_select_all: If True, the user can type an asterisk and get all items.
    :show_options: If True, prints out all options by giving the options to the prompt function.
    :show_options_first_time: If True, prints out all options if this is the user's first try.
    :close_enough: If True, will attempt to guess the user's intent.
    :close_enough_threshold: The maximum distance the guesses can have.
    :prompt_function: Can be overridden to create a custom prompt.
    :behavior_on_eof: Function that is called when input() raises an EOFError.
    '''
    user_inputs:list[str] = []
    options:list[str] = list(items.keys())
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
            print("Recognize %s so far." % (", ".join(successful_inputs),))
        if close_enough and len(user_inputs) > 0:
            pop_indices:list[int] = []
            guessed_items:list[tuple[str,str]] = []
            for index, item in enumerate(user_inputs):
                user_guess = guess_intent(item, options, close_enough_threshold)
                if user_guess is not None:
                    pop_indices.append(index)
                    guessed_items.append((item, user_guess))
                    successful_inputs.append(user_guess)
                    successful_set.add(user_guess)
            for index in reversed(pop_indices):
                user_inputs.pop(index)
            if len(guessed_items) > 0:
                print("Assuming %s." % (", ".join("\"%s\" means \"%s\"" % (user_input, guess) for user_input, guess in guessed_items),))
        should_retry = len(user_inputs) > 0
        if len(user_inputs) > 0:
            print("Cannot recognize %s." % (", ".join(user_inputs)))
    return [items[item] for item in successful_inputs]
