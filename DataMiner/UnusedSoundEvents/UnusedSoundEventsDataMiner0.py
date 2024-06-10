import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import DataMiner.UnusedSoundEvents.UnusedSoundEventsDataMiner as UnusedSoundEventsDataMiner
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class UnusedSoundEventsDataMiner0(UnusedSoundEventsDataMiner.UnusedSoundEventsDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("use_music_definitions", "a bool", True, bool),
    )

    def initialize(self, **kwargs) -> None:
        self.use_music_definitions:bool = kwargs["use_music_definitions"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.UnusedSoundEvents:
        sounds_json:DataMinerTyping.MySoundsJson = environment.dependency_data.get("sounds_json", self)
        sounds_json_sound_events = UnusedSoundEventsDataMiner.get_sounds_json_sound_events(sounds_json)

        sound_definitions:DataMinerTyping.SoundDefinitionsJson = environment.dependency_data.get("sound_definitions", self)
        sound_definitions_sound_events = list(sound_definitions.keys())

        if self.use_music_definitions:
            music_definitions:DataMinerTyping.MyMusicDefinitions = environment.dependency_data.get("music_definitions", self)
            music_definitions_sound_events = UnusedSoundEventsDataMiner.get_music_definitions_sound_events(music_definitions)

        all_sound_events = set(sounds_json_sound_events.keys())
        if self.use_music_definitions:
            all_sound_events.update(music_definitions_sound_events.keys())
        return sorted(sound_event for sound_event in sound_definitions_sound_events if sound_event not in all_sound_events)
