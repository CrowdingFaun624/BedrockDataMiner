import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.TextureList.TextureListDataMiner as TextureListDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class TextureListDataMiner0(TextureListDataMiner.TextureListDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("locations", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
    )

    def initialize(self, **kwargs) -> None:
        self.locations:list[str] = kwargs["locations"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[str,list[str]]:
        packs:DataMinerTyping.ResourcePacks = environment.dependency_data.get("resource_packs", self)
        pack_names = [(pack["name"], pack["path"]) for pack in packs]
        pack_files:dict[str,str] = {}
        for blocks_location in self.locations:
            pack_files.update({pack_path + blocks_location: pack_name for pack_name, pack_path in pack_names})
        files_request = [(file, "t", None) for file in pack_files.keys()]
        accessor = self.get_accessor("client")
        files:dict[str,str] = {key: value for key, value in self.read_files(accessor, files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        output = {pack_files[pack_file]: texture_list.splitlines() for pack_file, texture_list in files.items()}
        return Sorting.sort_everything(output)
