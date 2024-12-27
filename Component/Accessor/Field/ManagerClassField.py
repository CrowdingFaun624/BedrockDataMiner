import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter
import Downloader.DownloadManager as DownloadManager
import Downloader.DummyManager as DummyManager
import Downloader.Manager as Manager
import Downloader.StoredManager as StoredManager
import Utilities.Exceptions as Exceptions

BUILT_IN_MANAGER_CLASSES:dict[str,type[Manager.Manager]] = {manager_class.__name__: manager_class for manager_class in [
    DownloadManager.DownloadManager,
    DummyManager.DummyManager,
    StoredManager.StoredManager,
]}

MANAGER_CLASSES = ScriptImporter.import_scripted_types("managers/", BUILT_IN_MANAGER_CLASSES, Manager.Manager)

class ManagerClassField(Field.Field):

    def __init__(self, manager_class_str:str, path: list[str | int]) -> None:
        '''
        :manager_class_str: The name of the Manager class that this Field references.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        manager_class = MANAGER_CLASSES.get(manager_class_str)
        if manager_class is None:
            raise Exceptions.UnrecognizedManagerError(manager_class_str, self)
        self.manager_class = manager_class

    def get_final(self) -> type[Manager.Manager]:
        return self.manager_class
