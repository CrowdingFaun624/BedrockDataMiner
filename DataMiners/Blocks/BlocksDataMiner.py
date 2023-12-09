from typing import Any

import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class BlocksDataMiner(DataMiner.DataMiner):
    def activate(self, dependency_data: dict[str,Any]|None=None) -> list[DataMinerTyping.BlockTypedDict]:
        return super().activate(dependency_data)
