import Component.Field.Field as Field
import Domain.Domain as Domain
import Downloader.Manager as Manager
import Utilities.Exceptions as Exceptions


class ManagerClassField(Field.Field):

    __slots__ = (
        "manager_class",
    )

    def __init__(self, manager_class_str:str, domain:"Domain.Domain", path: list[str | int]) -> None:
        '''
        :manager_class_str: The name of the Manager class that this Field references.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        manager_class = domain.manager_classes.get(manager_class_str)
        if manager_class is None:
            raise Exceptions.UnrecognizedManagerError(manager_class_str, self)
        self.manager_class = manager_class

    def get_final(self) -> type[Manager.Manager]:
        return self.manager_class
