import json

import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.Splashes.SplashesDataMiner as SplashesDataMiner
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class SplashesDataMiner1(SplashesDataMiner.SplashesDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("splashes_location", "a str", True, str),
    )
    
    def initialize(self, **kwargs) -> None:
        self.splashes_location:str = kwargs["splashes_location"]
    
    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.Splashes:

        exception = None
        try:
            file = self.get_accessor("client").read(self.splashes_location, "t")
        except FileNotFoundError as e:
            exception = e
            exception.args = tuple(list(exception.args) + ["No splashes file found in \"%s\"!" % (self.version)])
        if exception is not None:
            raise exception
        
        splashes:DataMinerTyping.Splashes = json.loads(file)
        if not isinstance(splashes, dict):
            raise TypeError("Splashes in version \"%s\" is not a dict!" % (self.version))
        if list(splashes.keys()) != ["splashes"]:
            raise KeyError("Unrecognized key(s) are within version \"%s\": %s" % (self.version, list(splashes.keys())))
        output = {"vanilla": splashes["splashes"]}
        return Sorting.sort_everything(output)
