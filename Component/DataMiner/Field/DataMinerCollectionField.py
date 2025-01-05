import Component.Dataminer.AbstractDataminerCollectionComponent as AbstractDataminerCollectionComponent
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Pattern as Pattern


class DataminerCollectionField(ComponentField.ComponentField[AbstractDataminerCollectionComponent.AbstractDataminerCollectionComponent]):

    __slots__ = ()

    def __init__(self, subcomponent_data:str, path: list[str | int]) -> None:
        super().__init__(subcomponent_data, Pattern.Pattern("is_dataminer_collection"), path, allow_inline=Field.InlinePermissions.reference)
