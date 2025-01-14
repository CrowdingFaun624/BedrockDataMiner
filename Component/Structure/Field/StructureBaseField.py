import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.Structure.BaseComponent as BaseComponent
import Structure.StructureBase as StructureBase

STRUCTURE_BASE_PATTERN:Pattern.Pattern["BaseComponent.BaseComponent"] = Pattern.Pattern("is_base")

class StructureBaseField(ComponentField.ComponentField[BaseComponent.BaseComponent]):

    def __init__(self, subcomponent_data: str, path: list[str | int]) -> None:
        super().__init__(subcomponent_data, STRUCTURE_BASE_PATTERN, path, allow_inline=Field.InlinePermissions.reference)

    @property
    def final(self) -> StructureBase.StructureBase:
        return self.subcomponent.final
