from typing import TypeVar

import Component.Capabilities as Capabilities
import Component.Component as Component
import DataMiner.AbstractDataMinerCollection as AbstractDataMinerCollection

a = TypeVar("a", bound=AbstractDataMinerCollection.AbstractDataMinerCollection)

class AbstractDataMinerCollectionComponent(Component.Component[a]):

    class_name_article = "an AbstractDataMinerCollection"
    class_name = "AbstractDataMinerCollection"
    my_capabilities = Capabilities.Capabilities(is_dataminer_collection=True)

    disabled:bool = False
