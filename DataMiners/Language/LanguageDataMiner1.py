import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.Language.LanguageDataMiner as LanguageDataMiner
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class LanguageDataMiner1(LanguageDataMiner.LanguageDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("language_code", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("file_display_name", "a str", True, str),
    )

    def initialize(self, **kwargs) -> None:
        self.language_code:str = kwargs["language_code"]
        self.location:str = kwargs["location"]
        self.file_display_name:str|None = kwargs["file_display_name"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.Language:
        exception = None
        try:
            file = self.get_accessor("client").read(self.location % self.language_code, "t")
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
