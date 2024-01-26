import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.UnusedSoundEvents.UnusedSoundEventsDataMiner as UnusedSoundEventsDataMiner


class UnusedSoundEventsDataMiner0(UnusedSoundEventsDataMiner.UnusedSoundEventsDataMiner):

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.UnusedSoundEvents:
        sounds_json = dependency_data["sounds_json"]
        sounds_json_sound_events = UnusedSoundEventsDataMiner.get_sounds_json_sound_events(sounds_json)

        sound_definitions = dependency_data["sound_definitions"]
        sound_definitions_sound_events = list(sound_definitions.keys())

        music_definitions = dependency_data["music_definitions"]
        music_definitions_sound_events = UnusedSoundEventsDataMiner.get_music_definitions_sound_events(music_definitions)

        all_sound_events = set(sounds_json_sound_events.keys())
        all_sound_events.update(music_definitions_sound_events.keys())
        return sorted(sound_event for sound_event in sound_definitions_sound_events if sound_event not in all_sound_events)
