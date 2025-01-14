import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.Pattern as Pattern
import Dataminer.AbstractDataminerCollection as AbstractDataminerCollection

ABSTRACT_DATAMINER_COLLECTION_PATTERN:Pattern.Pattern["AbstractDataminerCollectionComponent"] = Pattern.Pattern("is_dataminer_collection")

class AbstractDataminerCollectionComponent[a: AbstractDataminerCollection.AbstractDataminerCollection](Component.Component[a]):

    class_name = "AbstractDataminerCollection"
    my_capabilities = Capabilities.Capabilities(is_dataminer_collection=True)

    disabled:bool = False

    __slots__ = ()
