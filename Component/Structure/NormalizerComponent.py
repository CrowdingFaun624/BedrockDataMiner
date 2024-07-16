import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.FunctionField as FunctionField
import Structure.Normalizer as Normalizer
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class NormalizerComponent(Component.Component[Normalizer.Normalizer]):

    class_name_article = "a Normalizer"
    class_name = "Normalizer"

    my_capabilities = Capabilities.Capabilities(is_function=True, is_normalizer=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("function_name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    def __init__(self, data:ComponentTyping.NormalizerTypedDict, name:str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data)

        self.arguments = data.get("arguments", {})

        self.children_has_normalizer = True

        self.function_field = FunctionField.FunctionField(data["function_name"], ["function_name"])
        self.function_field.check_arguments(self.arguments, ignore_parameters={"data"})
        self.fields.extend([self.function_field])

    def create_final(self) -> None:
        super().create_final()
        self.final = Normalizer.Normalizer(
            function=self.function_field.get_function(),
            arguments=self.arguments,
        )
