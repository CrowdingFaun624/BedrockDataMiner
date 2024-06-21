import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class TagComponent(Component.Component[str]):

    class_name_article = "a Tag"
    class_name = "Tag"
    my_capabilities = Capabilities.Capabilities(is_tag=True)
    children_has_normalizer = False
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    def __init__(self, data: ComponentTyping.TagTypedDict, name: str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data)

        self.final:str|None = None

    def create_final(self) -> None:
        super().create_final()
        self.final = self.name

    def __hash__(self) -> int:
        return hash(self.name)
