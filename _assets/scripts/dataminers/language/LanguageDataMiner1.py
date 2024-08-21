import _assets.scripts.dataminers.language.LanguageDataMiner as LanguageDataMiner
import _assets.scripts.dataminers.MyGrabSingleFileDataMiner as GrabSingleFileDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import _assets.scripts.dataminers.DataMinerTyping as DataMinerTyping
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["LanguageDataMiner1"]

class LanguageDataMiner1(GrabSingleFileDataMiner.MyGrabSingleFileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("language_code", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
    )

    def initialize(self, language_code:str, location:str) -> None:
        super().initialize(location % language_code, insert_pack="vanilla")

    def get_output(self, file: str, environment: DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.Language:
        lines = LanguageDataMiner.combine_lines(file.splitlines())
        output:dict[str,DataMinerTyping.LanguageTypedDict] = {}
        for line in lines:
            try:
                key, line_data = LanguageDataMiner.process_line(line)
            except Exception:
                raise Exceptions.DataMinerFailureError(self, "Failed to process line \"%s\"!" % (line,))
            if key is None or line_data is None: continue
            output[key] = line_data
        return super().get_output(output, environment)
