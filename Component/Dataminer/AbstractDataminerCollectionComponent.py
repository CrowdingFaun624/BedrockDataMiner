from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.Pattern import Pattern
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection

ABSTRACT_DATAMINER_COLLECTION_PATTERN:Pattern["AbstractDataminerCollectionComponent"] = Pattern("is_dataminer_collection")

class AbstractDataminerCollectionComponent[a: AbstractDataminerCollection](Component[a]):

    class_name = "AbstractDataminerCollection"
    my_capabilities = Capabilities(is_dataminer_collection=True)

    disabled:bool = False

    __slots__ = ()
