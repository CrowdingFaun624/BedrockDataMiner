from typing import TYPE_CHECKING

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.FieldListField as FieldListField
import Component.Pattern as Pattern
import Component.VersionTag.Field.VersionTagOrderAllowedChildrenField as VersionTagOrderAllowedChildrenField
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Version.VersionTag.VersionTagOrder as VersionTagOrder

if TYPE_CHECKING:
    import Component.VersionTag.VersionTagComponent as VersionTagComponent

VERSION_TAG_PATTERN:Pattern.Pattern["VersionTagComponent.VersionTagComponent"] = Pattern.Pattern([{"is_version_tag": True}])

class VersionTagOrderComponent(Component.Component[VersionTagOrder.VersionTagOrder]):

    class_name = "VersionTagOrder"
    class_name_article = "a VersionTagOrder"
    my_capabilities = Capabilities.Capabilities(is_version_tag_order=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("order", "a list", True, TypeVerifier.ListTypeVerifier(TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"), list, "a list", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("allowed_children", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"), "a dict", "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("top_level_tag", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("tags_before_top_level_tag", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("tags_after_top_level_tag", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
    )

    def __init__(self, data: ComponentTyping.VersionTagOrderTypedDict, name: str, component_group: str, index: int | None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data, name)

        self.order_field = FieldListField.FieldListField([
            ComponentListField.ComponentListField(tags, VERSION_TAG_PATTERN, ["order", index], allow_inline=Field.InLinePermissions.reference)
            for index, tags in enumerate(data["order"])
        ], ["order"])
        self.allowed_children_field = FieldListField.FieldListField([
            VersionTagOrderAllowedChildrenField.VersionTagOrderAllowedChildrenField(key, children, ["allowed_children", key])
            for key, children in data["allowed_children"].items()
        ], ["allowed_children"])
        self.top_level_tag_field = ComponentField.ComponentField(data["top_level_tag"], VERSION_TAG_PATTERN, ["top_level_tag"], allow_inline=Field.InLinePermissions.reference)
        self.tags_before_top_level_tag = ComponentListField.ComponentListField(data["tags_before_top_level_tag"], VERSION_TAG_PATTERN, ["tags_before_top_level_tag"], allow_inline=Field.InLinePermissions.reference)
        self.tags_after_top_level_tag = ComponentListField.ComponentListField(data["tags_after_top_level_tag"], VERSION_TAG_PATTERN, ["tags_after_top_level_tag"], allow_inline=Field.InLinePermissions.reference)
        self.fields.extend([self.order_field, self.allowed_children_field, self.top_level_tag_field, self.tags_before_top_level_tag, self.tags_after_top_level_tag])

    def create_final(self) -> None:
        super().create_final()
        self.final = VersionTagOrder.VersionTagOrder()

    def link_finals(self) -> None:
        super().link_finals()
        self.get_final().link_finals(
            order=list(self.order_field.map(lambda component_list_field: set(component_list_field.map(lambda version_tag_component: version_tag_component.get_final())))),
            allowed_children={version_tag_order_allowed_children_field.get_key().get_final(): list(version_tag_component.get_final() for version_tag_component in version_tag_order_allowed_children_field.get_children()) for version_tag_order_allowed_children_field in self.allowed_children_field},
            top_level_tag=self.top_level_tag_field.get_component().get_final(),
            tags_before_top_level_tag=list(self.tags_before_top_level_tag.map(lambda version_tag_component: version_tag_component.get_final())),
            tags_after_top_level_tag=list(self.tags_after_top_level_tag.map(lambda version_tag_component: version_tag_component.get_final())),
        )

    def check(self) -> list[Exception]:
        exceptions = super().check()
        used_version_tag_components:set["VersionTagComponent.VersionTagComponent"] = set()
        for order_set in self.order_field:
            used_version_tag_components.update(order_set.get_components())
        for allowed_children_subfield in self.allowed_children_field:
            used_version_tag_components.add(allowed_children_subfield.get_key())
            used_version_tag_components.update(allowed_children_subfield.get_children())
        used_version_tag_components.add(self.top_level_tag_field.get_component())
        used_version_tag_components.update(self.tags_before_top_level_tag.get_components())
        used_version_tag_components.update(self.tags_after_top_level_tag.get_components())
        for used_version_tag_component in used_version_tag_components:
            if not used_version_tag_component.is_order_tag:
                exceptions.append(Exceptions.NotAnOrderTagError(used_version_tag_component.get_final()))
        # rest of checking is in the ImporterEnvironment
        return exceptions
