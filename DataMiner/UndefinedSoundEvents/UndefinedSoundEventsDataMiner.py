import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import DataMiner.UnusedSoundEvents.UnusedSoundEventsDataMiner as UnusedSoundEventsDataMiner

get_sounds_json_sound_events = UnusedSoundEventsDataMiner.get_sounds_json_sound_events
get_music_definitions_sound_events = UnusedSoundEventsDataMiner.get_music_definitions_sound_events
add_items_to_output = UnusedSoundEventsDataMiner.add_items_to_output

class UndefinedSoundEventsDataMiner(DataMiner.DataMiner):

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.UndefinedSoundEvents:
        return super().activate(environment)
