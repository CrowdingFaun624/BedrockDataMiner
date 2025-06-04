from Component.Structure.AbstractPrimitiveStructureComponent import (
    AbstractPrimitiveStructureComponent,
)
from Structure.PrimitiveStructure import PrimitiveStructure


class PrimitiveStructureComponent(AbstractPrimitiveStructureComponent[PrimitiveStructure]):

    class_name = "Primitive"
    structure_type = PrimitiveStructure

    __slots__ = ()

    # No additional fields are necessary.
