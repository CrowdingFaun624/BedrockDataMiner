import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
from _assets.scripts.dataminers.UnusedSoundEventsDataMiner import (
    add_items_to_output, get_music_definitions_sound_events,
    get_sounds_json_sound_events)

__all__ = ["UndefinedSoundEventsDataMiner"]

class UndefinedSoundEventsDataMiner(DataMiner.DataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("use_music_definitions", "a bool", True, bool),
    )

    def initialize(self, use_music_definitions:bool) -> None:
        self.use_music_definitions = use_music_definitions

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.UndefinedSoundEvents:
        sounds_json:DataMinerTyping.MySoundsJson = environment.dependency_data.get("sounds_json", self)
        sounds_json_sound_events = get_sounds_json_sound_events(sounds_json)

        sound_definitions:DataMinerTyping.SoundDefinitionsJson = environment.dependency_data.get("sound_definitions", self)
        sound_definitions_sound_events = set(sound_definitions.keys())

        if self.use_music_definitions:
            music_definitions:DataMinerTyping.MyMusicDefinitions = environment.dependency_data.get("music_definitions", self)
            music_definitions_sound_events = get_music_definitions_sound_events(music_definitions)

        output:dict[str,list[list[str]]] = {}
        add_items_to_output(output, {sound_event: traces for sound_event, traces in sounds_json_sound_events.items() if sound_event not in sound_definitions_sound_events})
        if self.use_music_definitions:
            add_items_to_output(output, {sound_event: traces for sound_event, traces in music_definitions_sound_events.items() if sound_event not in sound_definitions_sound_events})

        return {key: value for key, value in sorted(output.items())}
