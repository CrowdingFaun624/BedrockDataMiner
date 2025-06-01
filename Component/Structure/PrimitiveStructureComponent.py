import Component.Structure.AbstractPrimitiveStructureComponent as AbstractPrimitiveStructureComponent
import Structure.PrimitiveStructure as PrimitiveStructure


class PrimitiveStructureComponent(AbstractPrimitiveStructureComponent.AbstractPrimitiveStructureComponent[PrimitiveStructure.PrimitiveStructure]):

    class_name = "Primitive"
    structure_type = PrimitiveStructure.PrimitiveStructure

    __slots__ = ()

    # No additional fields are necessary.
