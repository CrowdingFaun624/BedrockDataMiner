from typing import Generator, Iterable, TypeVar

import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataMinerParameters as DataMinerParameters
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.UndefinedSoundEvents.UndefinedSoundEventsDataMiner as UndefinedSoundEventsDataMiner

a, b = TypeVar("a"), TypeVar("b")
def glue_iterable(iter1:Iterable[a], iter2:Iterable[b]) -> Generator[a|b,None,None]:
    yield from iter1
    yield from iter2

class UndefinedSoundEventsDataMiner0(UndefinedSoundEventsDataMiner.UndefinedSoundEventsDataMiner):

    parameters = DataMinerParameters.TypedDictParameters({
        "use_music_definitions": (bool, True),
    })

    def initialize(self, **kwargs) -> None:
        self.use_music_definitions:bool = kwargs["use_music_definitions"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.UndefinedSoundEvents:
        sounds_json = environment.dependency_data["sounds_json"]
        assert sounds_json is not None
        sounds_json_sound_events = UndefinedSoundEventsDataMiner.get_sounds_json_sound_events(sounds_json)

        sound_definitions = environment.dependency_data["sound_definitions"]
        assert sound_definitions is not None
        sound_definitions_sound_events = set(sound_definitions.keys())

        if self.use_music_definitions:
            music_definitions = environment.dependency_data["music_definitions"]
            assert music_definitions is not None
            music_definitions_sound_events = UndefinedSoundEventsDataMiner.get_music_definitions_sound_events(music_definitions)

        output:dict[str,list[list[str]]] = {}
        UndefinedSoundEventsDataMiner.add_items_to_output(output, {sound_event: traces for sound_event, traces in sounds_json_sound_events.items() if sound_event not in sound_definitions_sound_events})
        if self.use_music_definitions:
            UndefinedSoundEventsDataMiner.add_items_to_output(output, {sound_event: traces for sound_event, traces in music_definitions_sound_events.items() if sound_event not in sound_definitions_sound_events})

        return {key: value for key, value in sorted(output.items())}
