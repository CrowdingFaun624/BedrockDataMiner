from typing import Any

import _assets.scripts.dataminers.GrabPackFileDataMiner as GrabPackFileDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import _assets.scripts.dataminers.DataMinerTyping as DataMinerTyping

__all__ = ["SoundDefinitionsDataMiner0"]

class SoundDefinitionsDataMiner0(GrabPackFileDataMiner.GrabPackFileDataMiner):

    def normalize(self, data:dict[str,Any]) -> dict[str,Any]:
        if "sound_definitions" in data:
            return data["sound_definitions"]
        else: return data

    def initialize(self) -> None:
        return super().initialize(["sounds/sound_definitions.json"], "resource_packs")

    def get_output(self, files: dict[str, dict[str,Any]], pack_files: dict[str, str], environment: DataMinerEnvironment.DataMinerEnvironment) -> dict[str, Any]:
        output:dict[str,dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]] = {}
        for file_name, sound_definitions in files.items():
            pack_name = pack_files[file_name]
            for sound_name, sound_properties in self.normalize(sound_definitions).items():
                if sound_name not in output:
                    output[sound_name] = {pack_name: sound_properties}
                else:
                    output[sound_name][pack_name] = sound_properties
        return output
