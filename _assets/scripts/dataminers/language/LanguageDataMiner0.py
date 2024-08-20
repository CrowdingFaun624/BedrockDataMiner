import _assets.scripts.dataminers.language.LanguageDataMiner as LanguageDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["LanguageDataMiner0"]

class LanguageDataMiner0(LanguageDataMiner.LanguageDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("language_code", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
    )

    def initialize(self, language_code:str, location:str) -> None:
        self.language_code = language_code
        self.location = location

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.Language:
        packs:DataMinerTyping.ResourcePacks = environment.dependency_data.get("resource_packs", self)
        pack_names = [(pack["name"], pack["path"]) for pack in packs]
        pack_files:dict[str,str] = {pack_path + self.location % (self.language_code,): pack_name for pack_name, pack_path in pack_names}
        files_request = [(file, "t", None) for file in pack_files.keys()]
        accessor = self.get_accessor("client", Accessor.DirectoryAccessor)
        files:dict[str,str] = {key: value for key, value in self.read_files(accessor, files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        output:DataMinerTyping.Language = {}
        for pack_file, language_file in files.items():
            resource_pack_name = pack_files[pack_file]
            lines = language_file.splitlines()
            resource_pack_output:dict[str,DataMinerTyping.LanguageTypedDict] = {}
            for line in lines:
                try:
                    key, line_data = self.process_line(line)
                except Exception:
                    raise Exceptions.DataMinerFailureError(self, "Failed to process line \"%s\" of pack \"%s\"!" % (line, pack_file))
                if key is None or line_data is None: continue
                resource_pack_output[key] = line_data
            output[resource_pack_name] = resource_pack_output

        return Sorting.sort_everything(output)
