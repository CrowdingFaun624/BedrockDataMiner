import Component.Field.Field as Field
import Dataminer.Dataminer as Dataminer
import Domain.Domain as Domain


class OptionalDataminerTypeField(Field.Field):

    __slots__ = (
        "dataminer",
    )

    def __init__(self, dataminer_name:str|None, domain:"Domain.Domain", path: list[str | int]) -> None:
        '''
        :dataminer_name: The name of the Dataminer referenced by this Field.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.dataminer = domain.dataminer_classes[dataminer_name] if dataminer_name is not None else Dataminer.NullDataminer

    def get_final(self) -> type[Dataminer.Dataminer]|type[Dataminer.NullDataminer]:
        return self.dataminer

    def exists(self) -> bool:
        "Returns True if this Field was initialized with a str, and False if it was initialized with None"
        return self.dataminer is not Dataminer.NullDataminer
