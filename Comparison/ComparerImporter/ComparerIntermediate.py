import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerSection as ComparerSection

class ComparerIntermediate(Intermediate.Intermediate): # just for type hints lol

    class_name_article = "a Comparer"
    class_name = "Comparer"

    my_type:list[type]

    def __init__(self, data: ComparerTyping.Comparers, name: str, index: int) -> None:
        self.name = name
        self.final:ComparerSection.ComparerSection|None = None
