import _assets.scripts.dataminers.GrabPackFileDataMiner as GrabPackFileDataMiner
import _assets.scripts.dataminers.language.LanguageDataMiner as LanguageDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import _assets.scripts.dataminers.DataMinerTyping as DataMinerTyping
import DataMiner.DataTypes as DataTypes
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["LanguageDataMiner0"]

class LanguageDataMiner0(GrabPackFileDataMiner.GrabPackFileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("language_code", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str", True, str),
    )

    def initialize(self, language_code:str, location:str) -> None:
        super().initialize([location % language_code], "resource_packs", DataTypes.DataTypes.json)
        self.language_code = language_code
        self.location = location

    def get_output(self, files: dict[str, str], pack_files: dict[str, str], environment: DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.Language:
        output:DataMinerTyping.Language = {}
        for pack_file, language_file in files.items():
            resource_pack_name = pack_files[pack_file]
            lines = language_file.splitlines()
            resource_pack_output:dict[str,DataMinerTyping.LanguageTypedDict] = {}
            for line in lines:
                try:
                    key, line_data = LanguageDataMiner.process_line(line)
                except Exception:
                    raise Exceptions.DataMinerFailureError(self, "Failed to process line \"%s\" of pack \"%s\"!" % (line, pack_file))
                if key is None or line_data is None: continue
                resource_pack_output[key] = line_data
            output[resource_pack_name] = resource_pack_output
        return output
