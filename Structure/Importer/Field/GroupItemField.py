import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.Field.FieldContainer as FieldContainer
import Structure.Importer.Field.OptionalComponentField as OptionalComponentField
import Structure.Importer.Field.TypeField as TypeField
import Structure.Importer.StructureComponent as StructureComponent

COMPONENT_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_structure": True}])

class GroupItemField(FieldContainer.FieldContainer):

    def __init__(self, key:str, value:str|None, path:list[str|int]) -> None:
        self.type_field = TypeField.TypeField(key, path)
        self.subcomponent_field:OptionalComponentField.OptionalComponentField[StructureComponent.StructureComponent] = OptionalComponentField.OptionalComponentField(value, COMPONENT_REQUEST_PROPERTIES, path)
        self.type_field.verify_with(self.subcomponent_field)
        super().__init__([self.type_field, self.subcomponent_field], path)

    def get_types(self) -> list[type]:
        return self.type_field.get_types()
    
    def get_component(self) -> StructureComponent.StructureComponent|None:
        return self.subcomponent_field.get_component()
