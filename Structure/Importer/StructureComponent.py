import Structure.Importer.Component as Component
import Structure.Importer.ImporterConfig as ImporterConfig
import Structure.Structure as Structure


class StructureComponent(Component.Component):

    class_name_article = "a StructureComponent"
    class_name = "StructureComponent"

    my_type:list[type]

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.final:Structure.Structure|None = None

    def check(self, config: ImporterConfig.ImporterConfig) -> list[Exception]:
        assert self.final is not None
        self.final.check_initialization_parameters()
        return super().check(config)
