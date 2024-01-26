import DataMiners.DataMiner as DataMiner
import DataMiners.UnusedSoundEvents.UnusedSoundEventsComparer as UnusedSoundEventsComparer
import DataMiners.UnusedSoundEvents.UnusedSoundEventsDataMiner0 as UnusedSoundEventsDataMiner0

dataminers = DataMiner.DataMinerCollection("unused_sound_events.json", "unused_sound_events", UnusedSoundEventsComparer.comparer, [
    DataMiner.DataMinerSettings("-", "-", UnusedSoundEventsDataMiner0.UnusedSoundEventsDataMiner0, ["music_definitions", "sound_definitions", "sounds_json"]),
])