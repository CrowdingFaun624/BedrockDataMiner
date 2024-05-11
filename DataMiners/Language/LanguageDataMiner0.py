import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.Language.LanguageDataMiner as LanguageDataMiner
import Utilities.Sorting as Sorting

class LanguageDataMiner0(LanguageDataMiner.LanguageDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "language_code": (str, True),
        "location": (str, True),
        "file_display_name": (str, True),
    })

    def initialize(self, **kwargs) -> None:
        self.language_code:str = kwargs["language_code"]
        self.location:str = kwargs["location"]
        self.file_display_name:str|None = kwargs["file_display_name"]

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.Language:
        packs = dependency_data["resource_packs"]
        assert packs is not None
        pack_names = [(pack["name"], pack["path"]) for pack in packs]
        pack_files:dict[str,str] = {pack_path + self.location % (self.language_code,): pack_name for pack_name, pack_path in pack_names}
        files_request = [(file, "t", None) for file in pack_files.keys()]
        files:dict[str,str] = {key: value for key, value in self.read_files(files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            if self.file_display_name is None:
                raise FileNotFoundError("No files found in \"%s\"" % self.version)
            else:
                raise FileNotFoundError("No %s files found in \"%s\"" % (self.file_display_name, self.version))

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
