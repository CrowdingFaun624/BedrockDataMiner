import string
from types import EllipsisType
from typing import Any, Sequence

from Component.Component import INVALID_NAME_CHARS, Component
from Component.Expression.ComponentExpression import ComponentExpression
from Component.Expression.ConcatenationExpression import ConcatenationExpression
from Component.Expression.Expression import Expression, Reader
from Component.Expression.Variable import Variable
from Component.Expression.VariableExpression import VariableExpression
from Utilities.Exceptions import (
    ExpressionParseError,
    ExpressionTrailingDataError,
    NotExpressionError,
)


def scan_for_expressions(data:Any, source_component:"Component", variables:dict[str,Variable], used_variables:set[str], is_key:bool=False) -> Any:
    '''
    Looks through the data and returns a copy where Expression strings have been replaced with Expressions.
    :data: The data to search for Expression strings.
    :component: The Component that the data belongs to.
    :variables: The Variables of the parent Component, if they exist. (Copy it.)
    '''
    match data:
        case str():
            if data.startswith("#"):
                reader = Reader(data[1:])
                output = parse_expression(reader, source_component, is_key)
                if not reader.at_last():
                    raise ExpressionTrailingDataError(data, source_component, reader.index)
                source_component.expressions.append(output)
                for variable_name in output.get_variables_used(variables):
                    used_variables.add(variable_name)
                    if variable_name not in variables:
                        variables[variable_name] = Variable(variable_name)
                return output
            elif data.startswith("\\#"):
                return data.removeprefix("\\") # escape for #
            else:
                return data
        case dict():
            return {scan_for_expressions(key, source_component, variables, used_variables, is_key=True): scan_for_expressions(value, source_component, variables, used_variables, is_key=is_key) for key, value in data.items()}
        case list():
            return [scan_for_expressions(item, source_component, variables, used_variables, is_key=is_key) for item in data]
        case Expression():
            # An Expression may be encountered if `source_component` is an inherited Component.
            output = data.copy(source_component)
            source_component.expressions.append(output)
            for variable_name in output.get_variables_used(variables):
                used_variables.add(variable_name)
                if variable_name not in variables:
                    variables[variable_name] = Variable(variable_name)
            return output
        case _:
            return data

INVALID_REFERENCE_CHARS = INVALID_NAME_CHARS.copy()
INVALID_REFERENCE_CHARS.discard("/")
INVALID_REFERENCE_CHARS.discard("!")
NUMBER_CHARACTERS = set(f"0123456789eE-.") # "e" is present for float literals.

def parse_expression(reader:Reader, source_component:Component, is_key:bool) -> Expression:
    output, _ = parse(reader, source_component, is_key)
    if not isinstance(output, Expression):
        raise NotExpressionError(reader.source)
    return output

def parse(reader:"Reader", source_component:Component, is_key:bool) -> tuple[Any, Sequence[Expression]]:
    '''
    Returns an appropriate Expression from `source`.
    '''
    start_index = reader.index
    first_char = reader.read(1, 1)
    output:Any|EllipsisType = ...
    output_expressions:Sequence[Expression]
    match first_char:
        case "{":
            output, output_expressions = parse_dict(reader, source_component, keys_require_quotes=True)
        case "[":
            output, output_expressions = parse_list(reader, source_component)
        case "'" | "\"":
            output, output_expressions = parse_string(reader), ()
        case "@" | "!":
            output, output_expressions = parse_component_reference(reader, source_component, is_key)
    if output is ...:
        pre_number_index = reader.index
        if first_char == "-" or first_char.isdigit():
            number_string = reader.read_while(lambda char: char in NUMBER_CHARACTERS)
            number_suffix = reader.read(1)
            if number_suffix == "i":
                output, output_expressions = int(number_string), ()
            elif number_suffix == "f":
                output, output_expressions = float(number_string), ()
            else: reader.set(pre_number_index) # some Component names may be number-like.
        if   not reader.at_last(4) and reader.read(4, 4) == "true":
            output, output_expressions = True, ()
        elif not reader.at_last(5) and reader.read(5, 5) == "false":
            output, output_expressions = False, ()
        elif not reader.at_last(4) and reader.read(4, 4) == "null":
            output, output_expressions = None, ()
    if output is ...:
        output, output_expressions = parse_variable(reader, source_component, is_key)
        parse_whitespace(reader)
    if not reader.at_last() and reader.read(1, 1) == "+":
        parse_whitespace(reader)
        other_expression = parse(reader, source_component, is_key)
        end_index = reader.index
        output = concatenation_expression = ConcatenationExpression(source_component, reader.select(start_index, end_index), output, other_expression)
        output_expressions = (concatenation_expression,)
    if output is ...:
        raise ExpressionParseError(reader, "(parser cannot recognize)")
    return output, output_expressions

def parse_whitespace(reader:Reader) -> None:
    reader.move_while(lambda char: char in string.whitespace)

def parse_component_reference(reader:Reader, source_component:Component, is_key:bool) -> tuple[ComponentExpression, Sequence[Expression]]:
    start_index = reader.index
    direct = reader.read(1) == "@"
    component_name = parse_component_name(reader)
    variables:dict[str,Any]|None
    # Expression may end without {}
    if not reader.at_last() and reader.read(1, 1) == "{":
        variables, subexpressions = parse_dict(reader, source_component, keys_require_quotes=False)
    else:
        variables = None
        subexpressions = ()
    end_index = reader.index
    output = ComponentExpression(source_component, reader.select(start_index, end_index), subexpressions, component_name, direct, variables)
    return output, (output,)

def parse_variable(reader:Reader, source_component:"Component", is_key:bool) -> tuple[Expression, Sequence[Expression]]:
    start_index = reader.index
    variable_name = reader.read_while(lambda char: char not in INVALID_NAME_CHARS)
    end_index = reader.index
    parse_whitespace(reader)
    output = VariableExpression(source_component, reader.select(start_index, end_index), is_key, variable_name)
    return output, (output,)

def parse_component_name(reader:Reader) -> str:
    return reader.read_while(lambda char: char not in INVALID_REFERENCE_CHARS)

def parse_key(reader:Reader, require_quotes:bool) -> str:
    if require_quotes or reader.read(1, 1) in "'\"":
        return parse_string(reader)
    else:
        return reader.read_while(lambda char: char not in INVALID_NAME_CHARS)

def parse_string(reader:Reader) -> str:
    char = reader.read(1)
    if char != "'":
        raise ExpressionParseError(reader, "because strings should start with a single quote")
    string:list[str] = []
    escaped:bool = False
    while True:
        char = reader.read(1)
        if not escaped and char == "\\":
            escaped = True
            continue
        elif not escaped and char == "'":
            break
        string.append(char)
    return "".join(string)

def parse_list(reader:Reader, source_component:Component) -> tuple[list[Any], Sequence[Expression]]:
    char = reader.read(1)
    if char != "[":
        raise ExpressionParseError(reader, "because lists should start with an opening square bracket")
    output:list[Any] = []
    if reader.read(1, 1) == "]":
        reader.move(1)
        return output, () # empty list
    expressions:list[Expression] = []
    while True:
        parse_whitespace(reader)
        value, subexpressions = parse(reader, source_component, False)
        expressions.extend(subexpressions)
        output.append(value)
        parse_whitespace(reader)
        char = reader.read(1)
        if char == "]":
            break
        elif char == ",":
            continue
    return output, expressions

def parse_dict(reader:Reader, source_component:Component, *, keys_require_quotes:bool) -> tuple[dict[str,Any], Sequence[Expression]]:
    if reader.read(1) != "{":
        raise ExpressionParseError(reader, "because of no \"{\" beginning the Expression")
    if reader.read(1, 1) == "}":
        reader.move(1)
        return {}, ()
    output:dict[str,Any] = {}
    expressions:list[Expression] = []
    while True:
        parse_whitespace(reader)
        key = parse_key(reader, keys_require_quotes)
        parse_whitespace(reader)
        if key in output:
            raise ExpressionParseError(reader, f"because \"{key}\" is duplicated")
        if reader.read(1) != "=":
            raise ExpressionParseError(reader, f"because an \"=\" was expected after key {key}")
        parse_whitespace(reader)
        value, subexpressions = parse(reader, source_component, False)
        expressions.extend(subexpressions)
        output[key] = value
        parse_whitespace(reader)
        char = reader.read(1)
        if char == "}":
            break
        elif char == ",":
            continue
        else: raise ExpressionParseError(reader, "because a \",\" or \"}\" was expected")
    return output, expressions
