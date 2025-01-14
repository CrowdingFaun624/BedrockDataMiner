import Dataminer.Dataminer as Dataminer
import Dataminer.DataminerEnvironment as DataminerEnvironment
import Dataminer.FileDataminer as FileDataminer
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier
from _domains.minecraft_bedrock.scripts.dataminers.PacksDataminer import \
    PackTypedDict

__all__ = ["PiecesDataminer"]

class PiecesDataminer(Dataminer.Dataminer):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("base_directory", True, str, function=FileDataminer.location_value_function),
        TypeVerifier.TypedDictKeyTypeVerifier("subdirectories", False, TypeVerifier.ListTypeVerifier(str, list, item_function=FileDataminer.location_item_function)),
        TypeVerifier.TypedDictKeyTypeVerifier("ignore_directories", False, TypeVerifier.ListTypeVerifier(str, list, item_function=FileDataminer.location_item_function)),
    )

    def initialize(self, base_directory:str, subdirectories:list[str]|None=None, ignore_directories:list[str]|None=None) -> None:
        self.base_directory = base_directory
        self.subdirectories = subdirectories if subdirectories is not None else []
        self.subdirectories.append("")
        self.ignore_directories = ignore_directories

    def activate(self, environment:DataminerEnvironment.DataminerEnvironment) -> list[PackTypedDict]:
        file_list:dict[str,str] = environment.dependency_data.get("all_files", self)
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
                pieces.append({"name": name, "path": f"{directory}{name}/"})
                break

        if len(pieces) == 0:
            raise Exceptions.DataminerNothingFoundError(self)
        return pieces
