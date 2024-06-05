import Structure.Importer.Component as Component
import Structure.Structure as Structure
import Utilities.Exceptions as Exceptions


class AbstractGroupComponent(Component.Component):

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.my_type:set[type] = set()
        self.final:dict[type,Structure.Structure|None]|None = None

    def get_subcomponents(self) -> list[Component.Component]:
        '''
        Returns a list of this Component's subcomponents.
        '''
        ...
    
    def get_final(self) -> dict[type,Structure.Structure|None]:
        if self.final is None:
            raise Exceptions.AttributeNoneError("final", self)
        return self.final
