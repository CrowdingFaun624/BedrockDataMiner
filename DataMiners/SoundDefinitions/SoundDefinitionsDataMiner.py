from typing import Any

import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class SoundDefinitionsDataMiner(DataMiner.DataMiner):
    def activate(self, dependency_data:dict[str,Any]|None=None) -> dict[str,dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]]:
        return super().activate(dependency_data)
