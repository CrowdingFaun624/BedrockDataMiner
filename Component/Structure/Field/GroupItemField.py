from typing import TYPE_CHECKING, Union

import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Field.FieldContainer as FieldContainer
import Component.Structure.Field.OptionalStructureComponentField as OptionalStructureComponentField
import Component.Structure.Field.TypeField as TypeField

if TYPE_CHECKING:
    import Component.Structure.StructureComponent as StructureComponent

class GroupItemField(FieldContainer.FieldContainer):

    __slots__ = (
        "subcomponent_field",
        "type_field",
    )

    def __init__(self, key:str, value:str|ComponentTyping.StructureTypedDicts|None, path:list[str|int], *, allow_inline:Field.InlinePermissions=Field.InlinePermissions.mixed) -> None:
        '''
        :key: The type associated with this GroupItemField.
        :value: The name of the reference Component or data of the inline Component for this type.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :allow_inline: An InlinePermissions object describing the type of subcomponent_data allowed.
        '''
        self.type_field = TypeField.TypeField(key, path)
        self.subcomponent_field = OptionalStructureComponentField.OptionalStructureComponentField(value, path, allow_inline=allow_inline)
        self.type_field.verify_with(self.subcomponent_field)
        super().__init__([self.type_field, self.subcomponent_field], path)

    def get_types(self) -> tuple[type,...]:
        return self.type_field.get_types()

    def get_component(self) -> Union["StructureComponent.StructureComponent",None]:
        return self.subcomponent_field.get_component()
