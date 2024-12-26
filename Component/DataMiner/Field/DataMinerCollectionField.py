import Component.DataMiner.AbstractDataMinerCollectionComponent as AbstractDataMinerCollectionComponent
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import DataMiner.AbstractDataMinerCollection as AbstractDataMinerCollection


class DataMinerCollectionField(ComponentField.ComponentField[AbstractDataMinerCollectionComponent.AbstractDataMinerCollectionComponent]):

    def __init__(self, subcomponent_data:str, path: list[str | int]) -> None:
        super().__init__(subcomponent_data, Pattern.Pattern([{"is_dataminer_collection": True}]), path, allow_inline=Field.InlinePermissions.reference)

    def get_final(self) -> AbstractDataMinerCollection.AbstractDataMinerCollection:
        return self.get_component().get_final()
