import DataMiners.DataMiner as DataMiner
import DataMiners.UndefinedSoundEvents.UndefinedSoundEventsComparer as UndefinedSoundEventsComparer
import DataMiners.UndefinedSoundEvents.UndefinedSoundEventsDataMiner0 as UndefinedSoundEventsDataMiner0

dataminers = DataMiner.DataMinerCollection("undefined_sound_events.json", "undefined_sound_events", UndefinedSoundEventsComparer.comparer, [
    DataMiner.DataMinerSettings("-", "-", UndefinedSoundEventsDataMiner0.UndefinedSoundEventsDataMiner0, ["music_definitions", "sound_definitions", "sounds_json"]),
])
