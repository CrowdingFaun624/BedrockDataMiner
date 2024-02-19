import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.UnusedSoundEvents.UnusedSoundEventsDataMiner as UnusedSoundEventsDataMiner

get_sounds_json_sound_events = UnusedSoundEventsDataMiner.get_sounds_json_sound_events
get_music_definitions_sound_events = UnusedSoundEventsDataMiner.get_music_definitions_sound_events
add_items_to_output = UnusedSoundEventsDataMiner.add_items_to_output

class UndefinedSoundEventsDataMiner(DataMiner.DataMiner):

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.UndefinedSoundEvents:
        return super().activate(dependency_data)
