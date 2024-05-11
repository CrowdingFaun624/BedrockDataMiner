import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.Language.LanguageDataMiner as LanguageDataMiner
import Utilities.Sorting as Sorting

class LanguageDataMiner1(LanguageDataMiner.LanguageDataMiner):

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
        exception = None
        try:
            file = self.read_file(self.location % self.language_code)
        except FileNotFoundError as e:
            exception = e
            if self.file_display_name is None:
                exception_message = "No file found in \"%s\"" % (self.version)
            else:
                exception_message = "No %s file found in \"%s\"!" % (self.file_display_name, self.version)
            exception.args = tuple(list(exception.args) + [exception_message])
        if exception is not None:
            raise exception

        output:DataMinerTyping.Language = {}
        lines = self.combine_lines(file.splitlines())
        resource_pack_output:dict[str,DataMinerTyping.LanguageTypedDict] = {}
        for line in lines:
            exception:Exception|None = None
            try:
                key, line_data = self.process_line(line)
            except Exception as e:
                exception = e
                exception.args = tuple(list(exception.args) + ["Failed to process line \"%s\"!" % (line,)])
            if exception is not None:
                raise exception
            if key is None or line_data is None: continue
            resource_pack_output[key] = line_data
        output["vanilla"] = resource_pack_output

        return Sorting.sort_everything(output)
