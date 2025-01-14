import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.FieldListField as FieldListField
import Component.Pattern as Pattern
import Component.VersionTag.Field.OptionalVersionTagField as OptionalVersionTagField
import Component.VersionTag.Field.VersionTagOrderAllowedChildrenField as VersionTagOrderAllowedChildrenField
import Component.VersionTag.VersionTagComponent as VersionTagComponent
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier
import Version.VersionTag.VersionTagOrder as VersionTagOrder

VERSION_TAG_PATTERN:Pattern.Pattern["VersionTagComponent.VersionTagComponent"] = Pattern.Pattern("is_version_tag")

class VersionTagOrderComponent(Component.Component[VersionTagOrder.VersionTagOrder]):

    class_name = "VersionTagOrder"
    class_name_article = "a VersionTagOrder"
    my_capabilities = Capabilities.Capabilities(is_version_tag_order=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("allowed_children", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"), "a dict", "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("order", "a list", True, TypeVerifier.ListTypeVerifier(TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"), list, "a list", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("tags_after_top_level_tag", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("tags_before_top_level_tag", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("top_level_tag", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    __slots__ = (
        "allowed_children_field",
        "order_field",
        "tags_after_top_level_tag",
        "tags_before_top_level_tag",
        "top_level_tag_field",
    )

    def initialize_fields(self, data: ComponentTyping.VersionTagOrderTypedDict) -> list[Field.Field]:
        self.order_field = FieldListField.FieldListField([
            ComponentListField.ComponentListField(tags, VERSION_TAG_PATTERN, ["order", index], allow_inline=Field.InlinePermissions.reference, assume_component_group="version_tags")
            for index, tags in enumerate(data["order"])
        ], ["order"])
        self.allowed_children_field = FieldListField.FieldListField([
            VersionTagOrderAllowedChildrenField.VersionTagOrderAllowedChildrenField(key, children, ["allowed_children", key])
            for key, children in data["allowed_children"].items()
        ], ["allowed_children"])
        self.top_level_tag_field = OptionalVersionTagField.OptionalVersionTagField(data["top_level_tag"], ["top_level_tag"])
        self.tags_before_top_level_tag = ComponentListField.ComponentListField(data["tags_before_top_level_tag"], VERSION_TAG_PATTERN, ["tags_before_top_level_tag"], allow_inline=Field.InlinePermissions.reference, assume_component_group="version_tags")
        self.tags_after_top_level_tag = ComponentListField.ComponentListField(data["tags_after_top_level_tag"], VERSION_TAG_PATTERN, ["tags_after_top_level_tag"], allow_inline=Field.InlinePermissions.reference, assume_component_group="version_tags")
        return [self.order_field, self.allowed_children_field, self.top_level_tag_field, self.tags_before_top_level_tag, self.tags_after_top_level_tag]

    def create_final(self) -> VersionTagOrder.VersionTagOrder:
        return VersionTagOrder.VersionTagOrder()

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.final.link_finals(
            order=list(self.order_field.map(lambda component_list_field: set(component_list_field.map(lambda version_tag_component: version_tag_component.final)))),
            allowed_children={
                version_tag_order_allowed_children_field.key_field.subcomponent.final: list(
                    version_tag_component.final
                    for version_tag_component in version_tag_order_allowed_children_field.children_field.subcomponents
                ) for version_tag_order_allowed_children_field in self.allowed_children_field
            },
            top_level_tag=self.top_level_tag_field.final,
            tags_before_top_level_tag=list(self.tags_before_top_level_tag.map(lambda version_tag_component: version_tag_component.final)),
            tags_after_top_level_tag=list(self.tags_after_top_level_tag.map(lambda version_tag_component: version_tag_component.final)),
        )
        return exceptions

    def check(self) -> list[Exception]:
        exceptions = super().check()
        used_version_tag_components:set["VersionTagComponent.VersionTagComponent"] = set()
        for order_set in self.order_field:
            used_version_tag_components.update(order_set.subcomponents)
        for allowed_children_subfield in self.allowed_children_field:
            used_version_tag_components.add(allowed_children_subfield.key_field.subcomponent)
            used_version_tag_components.update(allowed_children_subfield.children_field.subcomponents)
        if self.top_level_tag_field.subcomponent is not None:
            used_version_tag_components.add(self.top_level_tag_field.subcomponent)
        used_version_tag_components.update(self.tags_before_top_level_tag.subcomponents)
        used_version_tag_components.update(self.tags_after_top_level_tag.subcomponents)
        for used_version_tag_component in used_version_tag_components:
            if not used_version_tag_component.is_order_tag:
                exceptions.append(Exceptions.NotAnOrderTagError(used_version_tag_component.final))
        # rest of checking is in the ImporterEnvironment
        return exceptions
