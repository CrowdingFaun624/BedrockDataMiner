from typing import Callable

import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Utilities.TypeVerifier as TypeVerifier

class TagComponent(Component.Component):

    class_name_article = "a Tag"
    class_name = "Tag"

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier(("Tag",))),
    )
    my_properties = ComponentCapabilities.Capabilities(is_tag=True)

    children_has_normalizer = False

    def __init__(self, data: ComponentTyping.TagTypedDict, name: str, index: int) -> None:
        self.verify_arguments(data, name)
        self.name = name
        self.final:str|None = None

        self.links_to_other_components:list[Component.Component] = []
        self.parents:list[Component.Component] = []
    
    def set_component(self, components: dict[str, Component.Component], functions: dict[str, Callable]) -> None:
        pass

    def create_final(self) -> None:
        self.final = self.name
    
    def __hash__(self) -> int:
        return hash(self.name)
