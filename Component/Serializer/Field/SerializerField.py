import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.Serializer.SerializerComponent as SerializerComponent

SERIALIZER_PATTERN:Pattern.Pattern[SerializerComponent.SerializerComponent] = Pattern.Pattern("is_serializer")

class SerializerField(ComponentField.ComponentField[SerializerComponent.SerializerComponent]):
    
    __slots__ = ()
    
    def __init__(self, subcomponent_data:str, path: list[str | int]) -> None:
        super().__init__(subcomponent_data, SERIALIZER_PATTERN, path, allow_inline=Field.InlinePermissions.reference, assume_type="Serializer", assume_component_group="serializers")
