import json

import DataMiners.Credits.CreditsDataMiner as CreditsDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.Sorting as Sorting

class CreditsDataMiner0(CreditsDataMiner.CreditsDataMiner):
    
    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> dict[str, DataMinerTyping.Credits]:
        location = "credits/credits.json"

        exception = None
        try:
            file = self.read_file(location)
        except FileNotFoundError as e:
            exception = e
            exception.args = tuple(list(exception.args) + ["No \"credits.json\" file found in \"%s\"!" % (self.version)])
        if exception is not None:
            raise exception
        
        credits = json.loads(file)
        return Sorting.sort_everything(credits)
