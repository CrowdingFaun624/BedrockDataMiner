from typing import TYPE_CHECKING, Union

import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.Field as Field
import Structure.Importer.Field.FieldContainer as FieldContainer
import Structure.Importer.Field.OptionalStructureComponentField as OptionalStructureComponentField
import Structure.Importer.Field.TypeField as TypeField

if TYPE_CHECKING:
    import Structure.Importer.StructureComponent as StructureComponent

class GroupItemField(FieldContainer.FieldContainer):

    def __init__(self, key:str, value:str|ComponentTyping.StructureComponentTypedDicts|None, path:list[str|int], *, allow_in_line:Field.InLinePermissions=Field.InLinePermissions.mixed) -> None:
        '''
        :key: The type associated with this GroupItemField.
        :value: The name of the reference Component or data of the in-line Component for this type.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        :allow_in_line: An InLinePermissions object describing the type of subcomponent_data allowed.
        '''
        self.type_field = TypeField.TypeField(key, path)
        self.subcomponent_field = OptionalStructureComponentField.OptionalStructureComponentField(value, path, allow_in_line=allow_in_line)
        self.type_field.verify_with(self.subcomponent_field)
        super().__init__([self.type_field, self.subcomponent_field], path)

    def get_types(self) -> list[type]:
        return self.type_field.get_types()
    
    def get_component(self) -> Union["StructureComponent.StructureComponent",None]:
        return self.subcomponent_field.get_component()
