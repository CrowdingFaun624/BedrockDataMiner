import Component.Capabilities as Capabilities
import Component.Component as Component
import Dataminer.AbstractDataminerCollection as AbstractDataminerCollection


class AbstractDataminerCollectionComponent[a: AbstractDataminerCollection.AbstractDataminerCollection](Component.Component[a]):

    class_name_article = "an AbstractDataminerCollection"
    class_name = "AbstractDataminerCollection"
    my_capabilities = Capabilities.Capabilities(is_dataminer_collection=True)

    disabled:bool = False

    __slots__ = ()
