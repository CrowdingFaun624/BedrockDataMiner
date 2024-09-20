import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.FileDataMiner as FileDataMiner
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
from _assets.scripts.dataminers.PacksDataMiner import PackTypedDict

__all__ = ["PiecesDataMiner"]

class PiecesDataMiner(DataMiner.DataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("base_directory", "a str", True, str, function=FileDataMiner.location_value_function),
        TypeVerifier.TypedDictKeyTypeVerifier("subdirectories", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", item_function=FileDataMiner.location_item_function)),
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_directories", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", item_function=FileDataMiner.location_item_function)),
    )

    def initialize(self, base_directory:str, subdirectories:list[str]|None=None, ignore_directories:list[str]|None=None) -> None:
        self.base_directory = base_directory
        self.subdirectories = subdirectories if subdirectories is not None else []
        self.subdirectories.append("")
        self.ignore_directories = ignore_directories

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[PackTypedDict]:
        file_list:list[str] = environment.dependency_data.get("all_files", self)
        pieces:list[PackTypedDict] = []
        pieces_names:set[str] = set()

        for file in file_list:
            for subdirectory in self.subdirectories:
                directory = self.base_directory + subdirectory
                if not file.startswith(directory):
                    continue
                if self.ignore_directories is not None and any(file.startswith(ignore_directory) for ignore_directory in self.ignore_directories):
                    break
                name = file.removeprefix(directory).split("/", 1)[0]
                if name in pieces_names:
                    continue
                pieces.append({"name": name, "path": "%s%s/" % (directory, name)})
                break

        if len(pieces) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)
        return pieces
