from typing import Generator, Iterable, TypeVar

import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.UndefinedSoundEvents.UndefinedSoundEventsDataMiner as UndefinedSoundEventsDataMiner

a, b = TypeVar("a"), TypeVar("b")
def glue_iterable(iter1:Iterable[a], iter2:Iterable[b]) -> Generator[a|b,None,None]:
    yield from iter1
    yield from iter2

class UndefinedSoundEventsDataMiner0(UndefinedSoundEventsDataMiner.UndefinedSoundEventsDataMiner):

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.UndefinedSoundEvents:
        sounds_json = dependency_data["sounds_json"]
        sounds_json_sound_events = UndefinedSoundEventsDataMiner.get_sounds_json_sound_events(sounds_json)

        sound_definitions = dependency_data["sound_definitions"]
        sound_definitions_sound_events = set(sound_definitions.keys())

        music_definitions = dependency_data["music_definitions"]
        music_definitions_sound_events = UndefinedSoundEventsDataMiner.get_music_definitions_sound_events(music_definitions)

        output:dict[str,list[list[str]]] = {}
        UndefinedSoundEventsDataMiner.add_items_to_output(output, {sound_event: traces for sound_event, traces in sounds_json_sound_events.items() if sound_event not in sound_definitions_sound_events})
        UndefinedSoundEventsDataMiner.add_items_to_output(output, {sound_event: traces for sound_event, traces in music_definitions_sound_events.items() if sound_event not in sound_definitions_sound_events})

        return {key: value for key, value in sorted(output.items())}
