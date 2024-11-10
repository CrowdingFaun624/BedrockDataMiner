import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Structure.StructureTag as StructureTag
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class StructureTagComponent(Component.Component[StructureTag.StructureTag]):

    class_name = "StructureTag"
    class_name_article = "a StructureTag"
    my_capabilities = Capabilities.Capabilities(is_structure_tag=True)
    children_has_normalizer = False
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("is_file", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    def __init__(self, data: ComponentTyping.StructureTagTypedDict, name: str, component_group: str, index: int | None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data)

        self.is_file = data.get("is_file", False)

    def create_final(self) -> None:
        super().create_final()
        self.final = StructureTag.StructureTag(
            name=self.name,
            is_file=self.is_file,
        )

    def __hash__(self) -> int:
        return hash(self.name)
