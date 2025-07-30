from typing import Sequence

from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentFunctions import function_type_verifiers
from Component.ComponentTyping import FunctionTypedDict
from Component.Field.Field import Field
from Component.Field.FunctionField import FunctionField
from Component.Pattern import Pattern
from Structure.Function import Function
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

FUNCTION_PATTERN:Pattern["FunctionComponent"] = Pattern("is_function")

class FunctionComponent(Component[Function]):

    class_name = "Function"
    my_capabilities = Capabilities(is_function=True)

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("arguments", False, dict),
        TypedDictKeyTypeVerifier("function_name", True, str),
        TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "arguments",
        "function_field",
    )

    def initialize_fields(self, data: FunctionTypedDict) -> Sequence[Field]:
        self.arguments = data.get("arguments", {})

        self.function_field = FunctionField(data["function_name"], ("function_name",))

        return (self.function_field,)

    def create_final(self, trace:Trace) -> Function:
        return Function(
            name=self.name,
            full_name=self.full_name,
            trace_name=self.trace_name,
            function=self.function_field.function,
            arguments=self.arguments,
        )

    def check(self, trace: Trace) -> None:
        if (type_verifier := function_type_verifiers.get(self.function_field.function, None)) is not None:
            type_verifier.verify(self.arguments, trace)
