import json

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import DataMiner.Splashes.SplashesDataMiner as SplashesDataMiner
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class SplashesDataMiner1(SplashesDataMiner.SplashesDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("splashes_location", "a str", True, str),
    )
    
    def initialize(self, **kwargs) -> None:
        self.splashes_location:str = kwargs["splashes_location"]
    
    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.Splashes:

        accessor = self.get_accessor("client")
        if not accessor.file_exists(self.splashes_location):
            raise Exceptions.DataMinerNothingFoundError(self)
        file = self.get_accessor("client").read(self.splashes_location, "t")
        
        splashes:DataMinerTyping.Splashes = json.loads(file)
        if not isinstance(splashes, dict):
            raise Exceptions.DataMinerFailureError(self, "Splashes is not a dict!")
        if list(splashes.keys()) != ["splashes"]:
            raise Exceptions.DataMinerFailureError(self, "Unrecognized key(s): %s" % (list(splashes.keys())))
        output = {"vanilla": splashes["splashes"]}
        return Sorting.sort_everything(output)
