import string
from types import EllipsisType
from typing import Self

from Component.Component import Component
from Component.Expression.Expression import Expression, Reader
from Component.Expression.ExpressionContainer import ExpressionContainer
from Component.Expression.ExpressionParser import parse_expression
from Component.Expression.Variable import Variable
from Utilities.Exceptions import ExpressionParseError


class VariableReferenceExpression(ExpressionContainer):

    __slots__ = (
        "component_name",
        "variables",
    )

    def __init__(self, source_component: Component, component_name:str, source:str|None=None) -> None:
        super().__init__(source_component, source)
        self.component_name = component_name
        self.variables:dict[str,int|float|str|bool|None|Expression] = {}

    def copy(self, new_component: Component) -> "VariableReferenceExpression":
        output = VariableReferenceExpression(self.source_component, self.component_name, self.source)
        self.copy_attrs(output, new_component)
        return output

    def copy_attrs(self, new_expression: "VariableReferenceExpression", new_component: Component) -> None:
        super().copy_attrs(new_expression, new_component)
        new_expression.variables.update((key, (value.copy(new_component) if isinstance(value, Expression) else value)) for key, value in self.variables.items())
        new_expression.expressions.extend(value for value in new_expression.variables.values() if isinstance(value, Expression)) # Expressions were already copied in the line above.

    def evaluate(self, variables:dict[str,Variable]) -> dict[str,int|float|str|bool|None]:
        output:dict[str,int|float|str|bool|None] = {
            "inherit": self.component_name,
            "inheritance_type": "reference",
        }
        output.update((("$" + key, value.evaluate(variables) if isinstance(value, Expression) else value) for key, value in self.variables.items()))
        return output

    @classmethod
    def applicable(cls, reader: Reader, is_key: bool) -> bool:
        return "{" in reader.source

    @classmethod
    def parse(cls, reader:Reader, source_component: Component, is_key:bool) -> Self:
        component_name = reader.read_while(lambda char: char != "{")
        output = cls(source_component, component_name, reader.source) # VariableReferenceExpression can only appear as the whole Expression, so using reader.source will always give the correct answer.
        output.parse_reference_variables(reader)
        return output

    def parse_whitespace(self, reader:Reader) -> None:
        reader.move_while(lambda char: char in string.whitespace)

    def parse_key(self, reader:Reader) -> str:
        key_chars:list[str] = []
        while True:
            char = reader.read(1)
            if char in "= ":
                reader.move(-1)
                break
            key_chars.append(char)
        key = "".join(key_chars)
        return key

    def parse_string(self, reader:Reader) -> str|EllipsisType:
        char = reader.read(1)
        if char != "'":
            raise ExpressionParseError(reader, type(self), "because strings should start with a single quote")
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

    def parse_value(self, reader:Reader) -> int|float|str|bool|None|Expression|EllipsisType:
        first_char = reader.read(1, 1)
        if first_char in "'\"": # include double quote to get the error message from parse_string.
            return self.parse_string(reader)

        start_position = reader.index
        output_string = reader.read_while(lambda char: char not in ", }")
        output_number = None
        if len(output_string) >= 2 and (output_string[0].isnumeric() or output_string[0] == "-"):
            if output_string[-1] == "i":
                try:
                    output_number = int(output_string.removesuffix("i"))
                except ValueError:
                    pass
            if output_string[-1] == "f":
                try:
                    output_number = float(output_string.removesuffix("f"))
                except ValueError:
                    pass

        if output_number is not None:
            return output_number
        elif output_string == "false":
            return False
        elif output_string == "true":
            return True
        elif output_string == "null":
            return None

        reader.set(start_position)
        expression = parse_expression(reader, self.source_component)
        self.expressions.append(expression)
        return expression

    def parse_reference_variables(self, reader:Reader) -> None:
        if reader.read(1) != "{":
            raise ExpressionParseError(reader, type(self), "because of no \"{\" beginning the Expression")
        if reader.read(1, 1) == "}":
            return
        while True:
            self.parse_whitespace(reader)
            key = self.parse_key(reader)
            if key is ...:
                return
            self.parse_whitespace(reader)
            if key in self.variables:
                raise ExpressionParseError(reader, type(self), f"because \"{key}\" is duplicated")
            if reader.read(1) != "=":
                raise ExpressionParseError(reader, type(self), f"because an \"=\" was expected after key {key}")
            self.parse_whitespace(reader)
            value = self.parse_value(reader)
            if value is ...:
                return
            self.variables[key] = value
            self.parse_whitespace(reader)
            char = reader.read(1)
            if char == "}":
                break
            elif char == ",":
                continue
            else: raise ExpressionParseError(reader, type(self), "because a \",\" or \"}\" was expected")
