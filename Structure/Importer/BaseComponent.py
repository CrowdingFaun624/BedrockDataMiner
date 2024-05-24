from typing import Callable

import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.NormalizerComponent as NormalizerComponent
import Structure.Importer.StructureComponent as StructureComponent
import Structure.StructureBase as StructureBase
import Utilities.TypeVerifier as TypeVerifier

COMPONENT_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_structure": True}])
NORMALIZER_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_normalizer": True}])

class BaseComponent(Component.Component):

    class_name_article = "a Base"
    class_name = "Base"

    my_properties = ComponentCapabilities.Capabilities(is_base=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("imports", "a list", False, TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("from", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("components", "a dict", True, TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
                TypeVerifier.TypedDictKeyTypeVerifier("component", "a str", True, str),
                TypeVerifier.TypedDictKeyTypeVerifier("as", "a str", False, str),
            ), list, "a dict", "a list")),
        ), list, "a dict", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
    )

    def __init__(self, data:ComponentTyping.BaseComponentTypedDict, name:str) -> None:
        self.verify_arguments(data, name)

        self.name = name
        self.structure_name = data["name"]
        self.subcomponent_str = data["subcomponent"]
        self.normalizer_str = data.get("normalizer", None)
        self.post_normalizer_str = data.get("post_normalizer", None)
        self.imports = data.get("imports", None)

        self.subcomponent:StructureComponent.StructureComponent|None = None
        self.normalizer:NormalizerComponent.NormalizerComponent|None = None
        self.post_normalizer:NormalizerComponent.NormalizerComponent|None = None
        self.links_to_other_components:list[Component.Component] = []
        self.parents:list[Component.Component] = []
        self.final:StructureBase.StructureBase|None = None

        self.children_has_normalizer = False
        self.children_tags:set[str] = set()

    def set_component(self, components:dict[str,Component.Component], functions:dict[str,Callable]) -> None:
        self.subcomponent:StructureComponent.StructureComponent|None = self.choose_component(self.subcomponent_str, COMPONENT_REQUEST_PROPERTIES, components, ["subcomponent"])
        assert self.subcomponent is not None
        self.links_to_other_components.append(self.subcomponent)
        self.subcomponent.parents.append(self)
        if self.normalizer_str is None:
            self.normalizer = None
        else:
            self.normalizer:NormalizerComponent.NormalizerComponent|None = self.choose_component(self.normalizer_str, NORMALIZER_REQUEST_PROPERTIES, components, ["normalizer"])
            assert self.normalizer is not None
            self.links_to_other_components.append(self.normalizer)
            self.normalizer.parents.append(self)
        if self.post_normalizer_str is None:
            self.post_normalizer = None
        else:
            self.post_normalizer:NormalizerComponent.NormalizerComponent|None = self.choose_component(self.post_normalizer_str, NORMALIZER_REQUEST_PROPERTIES, components, ["post_normalizer"])
            assert self.post_normalizer is not None
            self.links_to_other_components.append(self.post_normalizer)
            self.post_normalizer.parents.append(self)

    def create_final(self) -> None:
        normalizer_final = None if self.normalizer is None else self.normalizer.final
        post_normalizer_final = None if self.post_normalizer is None else self.post_normalizer.final
        self.final = StructureBase.StructureBase(
            component_name=self.name,
            structure_name=self.structure_name,
            normalizer=normalizer_final,
            post_normalizer=post_normalizer_final,
            structure=None,
            children_tags=self.children_tags,
        )

    def link_finals(self) -> None:
        assert self.final is not None
        assert self.subcomponent is not None
        self.final.structure = self.subcomponent.final
