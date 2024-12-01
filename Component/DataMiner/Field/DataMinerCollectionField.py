import Component.DataMiner.DataMinerCollectionComponent as DataMinerCollectionComponent
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import DataMiner.DataMinerCollection as DataMinerCollection


class DataMinerCollectionField(ComponentField.ComponentField[DataMinerCollectionComponent.DataMinerCollectionComponent]):

    def __init__(self, subcomponent_data:str, path: list[str | int]) -> None:
        super().__init__(subcomponent_data, Pattern.Pattern([{"is_dataminer_collection": True}]), path, allow_inline=Field.InlinePermissions.reference)

    def get_final(self) -> DataMinerCollection.DataMinerCollection:
        return self.get_component().get_final()
