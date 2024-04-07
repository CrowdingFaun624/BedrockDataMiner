from typing import Callable

import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.StructureComponent as StructureComponent
import Structure.Importer.TypeAliasComponent as TypeAliasComponent
import Structure.Structure as Structure
import Utilities.TypeVerifier as TypeVerifier

COMPONENT_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_structure": True}])
TYPE_ALIAS_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_type_alias": True}])

class GroupComponent(Component.Component):

    class_name_article = "a Group"
    class_name = "Group"

    my_properties = ComponentCapabilities.Capabilities(is_group=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
            TypeVerifier.TypedDictKeyTypeVerifier("subcomponents", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, (str, type(None)), "a dict", "a str", "a str or None")),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("index", "an int", True, int),
    )

    def __init__(self, data:ComponentTyping.GroupComponentTypedDict, name:str, index:int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index}, ["%s \"%s\"" % (self.class_name, name)])

        self.name = name
        self.subcomponents_strs = data["subcomponents"]

        self.subcomponents:list[tuple[type|TypeAliasComponent.TypeAliasComponent,StructureComponent.StructureComponent|None]]|None = None
        self.links_to_other_components:list[Component.Component] = []
        self.parents:list[Component.Component] = []
        self.my_type:set[type] = set()
        self.check_types_final:list[tuple[list[type], StructureComponent.StructureComponent|None]]|None = None
        self.final:dict[type,Structure.Structure|None]|None = None

        self.children_has_normalizer = False

    def set_component(self, components:dict[str,Component.Component], functions:dict[str,Callable]) -> None:
        self.subcomponents = []
        already_types:set[str] = set()
        for type_str, subcomponent_str in self.subcomponents_strs.items():
            subcomponent:StructureComponent.StructureComponent|None
            subcomponent_type:TypeAliasComponent.TypeAliasComponent|type
            if type_str in already_types:
                raise KeyError("Duplicate type \"%s\" of %s \"%s\"." % (type_str, self.class_name, self.name))
            already_types.add(type_str)
            if type_str in ComponentTyping.DEFAULT_TYPES:
                subcomponent_type = ComponentTyping.DEFAULT_TYPES[type_str]
                self.my_type.add(subcomponent_type)
            else:
                subcomponent_type = self.choose_component(type_str, TYPE_ALIAS_REQUEST_PROPERTIES, components, ["subcomponents", type_str])
                assert isinstance(subcomponent_type, TypeAliasComponent.TypeAliasComponent)
                self.links_to_other_components.append(subcomponent_type)
                subcomponent_type.parents.append(self)
                assert subcomponent_type.types is not None
                self.my_type.update(subcomponent_type.types)
            if subcomponent_str is None:
                subcomponent = None
            else:
                subcomponent = self.choose_component(subcomponent_str, COMPONENT_REQUEST_PROPERTIES, components, ["subcomponents", type_str])
                assert subcomponent is not None
                self.links_to_other_components.append(subcomponent)
                subcomponent.parents.append(self)
            self.subcomponents.append((subcomponent_type, subcomponent))

    def create_final(self) -> None:
        self.final = {}

    def link_finals(self) -> None:
        assert self.subcomponents is not None
        assert self.final is not None
        self.check_types_final = []
        for subcomponent_type, subcomponent in self.subcomponents:
            valid_types:list[type]
            if isinstance(subcomponent_type, type):
                valid_types = [subcomponent_type]
            elif isinstance(subcomponent_type, TypeAliasComponent.TypeAliasComponent):
                assert subcomponent_type.types is not None
                valid_types = subcomponent_type.types
            if subcomponent is None:
                structure = None
            else:
                structure = subcomponent.final
            for valid_type in valid_types:
                self.final[valid_type] = structure
            self.check_types_final.append((valid_types, subcomponent))

    def check(self) -> list[Exception]|None:
        assert self.check_types_final is not None
        for index, (types, subcomponent) in enumerate(self.check_types_final):
            if subcomponent is None:
                for type_item in types:
                    if type_item in ComponentTyping.REQUIRES_SUBCOMPONENT_TYPES:
                        return [TypeError("Item %i of %s \"%s\" accepts type %s, but has a null Subcomponent!" % (index, self.class_name, self.name, type_item.__name__))]
            else:
                for type_item in types:
                    if type_item not in subcomponent.my_type:
                        its_types = ", ".join(its_type.__name__ for its_type in subcomponent.my_type)
                        return [TypeError("Item %i of %s \"%s\" accepts type %s, but its Subcomponent, \"%s\", only accepts type [%s]!" % (index, self.class_name, self.name, type_item.__name__, subcomponent.name, its_types))]
