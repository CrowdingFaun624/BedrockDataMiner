import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.UnusedSoundEvents.UnusedSoundEventsDataMiner as UnusedSoundEventsDataMiner


class UnusedSoundEventsDataMiner0(UnusedSoundEventsDataMiner.UnusedSoundEventsDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "use_music_definitions": (bool, True),
    })

    def initialize(self, **kwargs) -> None:
        self.use_music_definitions:bool = kwargs["use_music_definitions"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.UnusedSoundEvents:
        sounds_json = environment.dependency_data["sounds_json"]
        assert sounds_json is not None
        sounds_json_sound_events = UnusedSoundEventsDataMiner.get_sounds_json_sound_events(sounds_json)

        sound_definitions = environment.dependency_data["sound_definitions"]
        assert sound_definitions is not None
        sound_definitions_sound_events = list(sound_definitions.keys())

        if self.use_music_definitions:
            music_definitions = environment.dependency_data["music_definitions"]
            assert music_definitions is not None
            music_definitions_sound_events = UnusedSoundEventsDataMiner.get_music_definitions_sound_events(music_definitions)

        all_sound_events = set(sounds_json_sound_events.keys())
        if self.use_music_definitions:
            all_sound_events.update(music_definitions_sound_events.keys())
        return sorted(sound_event for sound_event in sound_definitions_sound_events if sound_event not in all_sound_events)
