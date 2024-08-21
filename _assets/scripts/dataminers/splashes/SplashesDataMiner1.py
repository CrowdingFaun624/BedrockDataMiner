import _assets.scripts.dataminers.MyGrabSingleFileDataMiner as MyGrabSingleFileDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import _assets.scripts.dataminers.DataMinerTyping as DataMinerTyping
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["SplashesDataMiner1"]

class SplashesDataMiner1(MyGrabSingleFileDataMiner.MyGrabSingleFileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("location", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def initialize(self, locations:str|list[str]) -> None:
        super().initialize(locations, insert_pack="vanilla")
        self.splashes_location = locations

    def get_output(self, file:DataMinerTyping.Splashes, environment: DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.Splashes:
        if not isinstance(file, dict):
            raise Exceptions.DataMinerFailureError(self, "Splashes is not a dict!")
        if list(file.keys()) != ["splashes"]:
            raise Exceptions.DataMinerFailureError(self, "Unrecognized key(s): %s" % (list(file.keys())))
        output = file["splashes"]
        return super().get_output(output, environment)
