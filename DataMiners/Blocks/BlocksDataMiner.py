from typing import Any

import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class BlocksDataMiner(DataMiner.DataMiner):
    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict|None=None) -> dict[str,dict[str,DataMinerTyping.BlocksJsonBlockTypedDict]]:
        return super().activate(dependency_data)
