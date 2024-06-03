import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.Language.LanguageDataMiner as LanguageDataMiner
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class LanguageDataMiner0(LanguageDataMiner.LanguageDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("language_code", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
    )

    def initialize(self, **kwargs) -> None:
        self.language_code:str = kwargs["language_code"]
        self.location:str = kwargs["location"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.Language:
        packs = environment.dependency_data["resource_packs"]
        assert packs is not None
        pack_names = [(pack["name"], pack["path"]) for pack in packs]
        pack_files:dict[str,str] = {pack_path + self.location % (self.language_code,): pack_name for pack_name, pack_path in pack_names}
        files_request = [(file, "t", None) for file in pack_files.keys()]
        accessor = self.get_accessor("client")
        files:dict[str,str] = {key: value for key, value in self.read_files(accessor, files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise FileNotFoundError("No files found in \"%s\"" % self.version)

        output:DataMinerTyping.Language = {}
        for pack_file, language_file in files.items():
            resource_pack_name = pack_files[pack_file]
            lines = language_file.splitlines()
            resource_pack_output:dict[str,DataMinerTyping.LanguageTypedDict] = {}
            for line in lines:
                exception:Exception|None = None
                try:
                    key, line_data = self.process_line(line)
                except Exception as e:
                    exception = e
                    exception.args = tuple(list(exception.args) + ["Failed to process line \"%s\" of pack \"%s\"!" % (line, pack_file)])
                if exception is not None:
                    raise exception
                if key is None or line_data is None: continue
                resource_pack_output[key] = line_data
            output[resource_pack_name] = resource_pack_output

        return Sorting.sort_everything(output)
