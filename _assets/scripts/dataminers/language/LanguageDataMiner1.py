import _assets.scripts.dataminers.language.LanguageDataMiner as LanguageDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["LanguageDataMiner1"]

class LanguageDataMiner1(LanguageDataMiner.LanguageDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("language_code", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
    )

    def initialize(self, language_code:str, location:str) -> None:
        self.language_code = language_code
        self.location = location

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.Language:
        accessor = self.get_accessor("client", Accessor.DirectoryAccessor)
        if not accessor.file_exists(self.location % self.language_code):
            raise Exceptions.DataMinerNothingFoundError(self)
        file = accessor.read(self.location % self.language_code, "t")

        output:DataMinerTyping.Language = {}
        lines = self.combine_lines(file.splitlines())
        resource_pack_output:dict[str,DataMinerTyping.LanguageTypedDict] = {}
        for line in lines:
            try:
                key, line_data = self.process_line(line)
            except Exception:
                raise Exceptions.DataMinerFailureError(self, "Failed to process line \"%s\"!" % (line,))
            if key is None or line_data is None: continue
            resource_pack_output[key] = line_data
        output["vanilla"] = resource_pack_output

        return Sorting.sort_everything(output)
