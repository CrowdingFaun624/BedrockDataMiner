import Component.Capabilities as Capabilities
import Component.Component as Component
import DataMiner.AbstractDataMinerCollection as AbstractDataMinerCollection


class AbstractDataMinerCollectionComponent[a: AbstractDataMinerCollection.AbstractDataMinerCollection](Component.Component[a]):

    class_name_article = "an AbstractDataMinerCollection"
    class_name = "AbstractDataMinerCollection"
    my_capabilities = Capabilities.Capabilities(is_dataminer_collection=True)

    disabled:bool = False

    __slots__ = ()
