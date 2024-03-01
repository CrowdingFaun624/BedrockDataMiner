from typing import Any

import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class GrabPackFileDataMiner(DataMiner.DataMiner):

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> Any:
        return super().activate(dependency_data)
