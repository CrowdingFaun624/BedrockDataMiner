from typing import Generator, Iterable, TypeVar

import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.UndefinedSoundEvents.UndefinedSoundEventsDataMiner as UndefinedSoundEventsDataMiner
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

a, b = TypeVar("a"), TypeVar("b")
def glue_iterable(iter1:Iterable[a], iter2:Iterable[b]) -> Generator[a|b,None,None]:
    yield from iter1
    yield from iter2

class UndefinedSoundEventsDataMiner0(UndefinedSoundEventsDataMiner.UndefinedSoundEventsDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("use_music_definitions", "a bool", True, bool),
    )

    def initialize(self, **kwargs) -> None:
        self.use_music_definitions:bool = kwargs["use_music_definitions"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.UndefinedSoundEvents:
        sounds_json:DataMinerTyping.MySoundsJson = environment.dependency_data.get("sounds_json", self)
        sounds_json_sound_events = UndefinedSoundEventsDataMiner.get_sounds_json_sound_events(sounds_json)

        sound_definitions:DataMinerTyping.SoundDefinitionsJson = environment.dependency_data.get("sound_definitions", self)
        sound_definitions_sound_events = set(sound_definitions.keys())

        if self.use_music_definitions:
            music_definitions:DataMinerTyping.MyMusicDefinitions = environment.dependency_data.get("music_definitions", self)
            music_definitions_sound_events = UndefinedSoundEventsDataMiner.get_music_definitions_sound_events(music_definitions)

        output:dict[str,list[list[str]]] = {}
        UndefinedSoundEventsDataMiner.add_items_to_output(output, {sound_event: traces for sound_event, traces in sounds_json_sound_events.items() if sound_event not in sound_definitions_sound_events})
        if self.use_music_definitions:
            UndefinedSoundEventsDataMiner.add_items_to_output(output, {sound_event: traces for sound_event, traces in music_definitions_sound_events.items() if sound_event not in sound_definitions_sound_events})

        return {key: value for key, value in sorted(output.items())}
