import Structure.Structure as Structure
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Component as Component

class StructureComponent(Component.Component): # just for type hints lol

    class_name_article = "a StructureComponent"
    class_name = "StructureComponent"

    my_type:list[type]

    def __init__(self, data: ComponentTyping.StructureComponentTypedDicts, name: str, index: int) -> None:
        self.name = name
        self.final:Structure.Structure|None = None
