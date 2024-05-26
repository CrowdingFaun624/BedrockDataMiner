from typing import Any

import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerEnvironment as DataMinerEnvironment


class GrabPackFileDataMiner(DataMiner.DataMiner):

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> Any:
        return super().activate(environment)
