import Structure.Importer.Component as Component
import Structure.Structure as Structure


class AbstractGroupComponent(Component.Component):

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.my_type:set[type] = set()
        self.final:dict[type,Structure.Structure|None]|None = None
