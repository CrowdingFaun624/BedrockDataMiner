import DataMiner.BuiltIns.GrabSingleFileDataMiner as GrabSingleFileDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import _assets.scripts.dataminers.DataMinerTyping as DataMinerTyping

__all__ = ["SoundDefinitionsDataMiner1"]

class SoundDefinitionsDataMiner1(GrabSingleFileDataMiner.GrabSingleFileDataMiner):

    def initialize(self) -> None:
        return super().initialize(["sounds/sounds.json"])

    def get_output(self, file:dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict], environment: DataMinerEnvironment.DataMinerEnvironment) -> dict[str,dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]]:
        output:dict[str,dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]] = {}
        for sound_name, sound_properties in file.items():
            output[sound_name] = {"vanilla": sound_properties}
        return output
