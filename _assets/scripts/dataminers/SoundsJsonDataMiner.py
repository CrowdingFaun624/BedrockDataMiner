from typing import IO, Any, Callable, cast

import pyjson5  # supports comments

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import DataMiner.FileDataMiner as FileDataMiner
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["SoundsJsonDataMiner"]

class SoundsJsonDataMiner(FileDataMiner.FileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("sounds_json_locations", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
    )

    def initialize(self, sounds_json_locations:list[str]) -> None:
        self.sounds_json_locations = sounds_json_locations

    def parse_flat_sound_collection(self, source:DataMinerTyping.SoundsJsonFlatCollectionTypedDict, destination:DataMinerTyping.ResourcePackSoundsJsonFlatCollectionTypedDict, resource_pack_name:str) -> None:
        if list(source.keys()) != ["events"]:
            raise Exceptions.DataMinerFailureError(self, "Invalid keys in a flat sound collection in \"%s\": %s" % (resource_pack_name, str(list(source.keys()))))
        if "events" not in destination: destination["events"] = {}
        if "events" in source:
            for event_name, event_properties in source["events"].items():
                if event_name not in destination["events"]:
                    destination["events"][event_name] = {resource_pack_name: event_properties}
                else:
                    destination["events"][event_name][resource_pack_name] = event_properties

    def parse_sound_collection(self, source:DataMinerTyping.SoundsJsonSoundCollectionTypedDict, destination:DataMinerTyping.ResourcePackSoundsJsonSoundCollectionTypedDict, resource_pack_name:str) -> None:
        if len(set(source.keys()) - set(("events", "volume", "pitch"))) > 0:
            raise Exceptions.DataMinerFailureError(self, "Invalid keys in a sound collection in \"%s\": %s" % (resource_pack_name, str(list(source.keys()))))
        if "events" not in destination: destination["events"] = {}
        if "volume" not in destination: destination["volume"] = {}
        if "pitch" not in destination: destination["pitch"] = {}
        if "volume" in source:
            destination["volume"][resource_pack_name] = source["volume"]
        if "pitch" in source:
            destination["pitch"][resource_pack_name] = source["pitch"]
        if "events" in source:
            for event_name, event_properties in source["events"].items():
                if event_name not in destination["events"]:
                    destination["events"][event_name] = {resource_pack_name: event_properties}
                else:
                    destination["events"][event_name][resource_pack_name] = event_properties

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.MySoundsJsonTypedDict:
        resource_packs:DataMinerTyping.ResourcePacks = environment.dependency_data.get("resource_packs", self)
        resource_pack_names = [(resource_pack["name"], resource_pack["path"]) for resource_pack in resource_packs]
        resource_pack_files:dict[str,str] = {}
        for sounds_json_location in self.sounds_json_locations:
            resource_pack_files.update({resource_pack_path + sounds_json_location: resource_pack_name for resource_pack_name, resource_pack_path in resource_pack_names})
        files_request = [(resource_pack_file, "t", cast(Callable[[IO[str]],Any], pyjson5.load)) for resource_pack_file in resource_pack_files.keys()]
        accessor = self.get_accessor("client")
        files:dict[str,DataMinerTyping.SoundsJsonTypedDict] = {key: value for key, value in self.read_files(accessor, files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        sounds_json:DataMinerTyping.MySoundsJsonTypedDict = {
            "individual_event_sounds": {},
            "block_sounds": {},
            "interactive_block_sounds": {},
            "entity_sounds": {},
            "interactive_entity_sounds": {},
        }
        for resource_pack_file, resource_pack_sounds_json in files.items():
            resource_pack_name = resource_pack_files[resource_pack_file]

            # individual_event_sounds
            if "individual_event_sounds" in resource_pack_sounds_json:
                self.parse_flat_sound_collection(resource_pack_sounds_json["individual_event_sounds"], sounds_json["individual_event_sounds"], resource_pack_name)

            # block_sounds
            if "block_sounds" in resource_pack_sounds_json:
                for block_sound_type_name, block_sound_type_properties in resource_pack_sounds_json["block_sounds"].items():
                    if block_sound_type_name not in sounds_json["block_sounds"]:
                        sounds_json["block_sounds"][block_sound_type_name] = {}
                    self.parse_sound_collection(block_sound_type_properties, sounds_json["block_sounds"][block_sound_type_name], resource_pack_name)

            # interactive_block_sounds
            if "interactive_sounds" in resource_pack_sounds_json and "block_sounds" in resource_pack_sounds_json["interactive_sounds"]:
                for block_sound_type_name, block_sound_type_properties in resource_pack_sounds_json["interactive_sounds"]["block_sounds"].items():
                    if block_sound_type_name not in sounds_json["interactive_block_sounds"]:
                        sounds_json["interactive_block_sounds"][block_sound_type_name] = {}
                    self.parse_sound_collection(block_sound_type_properties, sounds_json["interactive_block_sounds"][block_sound_type_name], resource_pack_name)

            # entity_sounds
            if "entity_sounds" in resource_pack_sounds_json:
                if "defaults" in resource_pack_sounds_json["entity_sounds"]:
                    if "defaults" not in sounds_json["entity_sounds"]:
                        sounds_json["entity_sounds"]["defaults"] = {}
                    self.parse_sound_collection(resource_pack_sounds_json["entity_sounds"]["defaults"], sounds_json["entity_sounds"]["defaults"], resource_pack_name)
                if "entities" in resource_pack_sounds_json["entity_sounds"]:
                    for entity_name, entity_sounds in resource_pack_sounds_json["entity_sounds"]["entities"].items():
                        if entity_name == "defaults": raise Exceptions.DataMinerFailureError(self, "An entity named \"defaults\" clashes with the separate defaults object in %s!" % (resource_pack_name,))
                        if entity_name not in sounds_json["entity_sounds"]:
                            sounds_json["entity_sounds"][entity_name] = {}
                        self.parse_sound_collection(entity_sounds, sounds_json["entity_sounds"][entity_name], resource_pack_name)

            # interactive_entity_sounds
            if "interactive_sounds" in resource_pack_sounds_json and "entity_sounds" in resource_pack_sounds_json["interactive_sounds"]:
                if "defaults" in resource_pack_sounds_json["interactive_sounds"]["entity_sounds"]:
                    if "defaults" not in sounds_json["interactive_entity_sounds"]:
                        sounds_json["interactive_entity_sounds"]["defaults"] = {}
                    self.parse_sound_collection(resource_pack_sounds_json["interactive_sounds"]["entity_sounds"]["defaults"], sounds_json["entity_sounds"]["defaults"], resource_pack_name)
                if "entities" in resource_pack_sounds_json["interactive_sounds"]["entity_sounds"]:
                    for entity_name, entity_sounds in resource_pack_sounds_json["interactive_sounds"]["entity_sounds"]["entities"].items():
                        if entity_name == "defaults": raise Exceptions.DataMinerFailureError(self, "An interactive entity named \"defaults\" clashes withe the separate defaults object in %s!" % (resource_pack_name))
                        if entity_name not in sounds_json["interactive_entity_sounds"]:
                            sounds_json["interactive_entity_sounds"][entity_name] = {}
                        self.parse_sound_collection(entity_sounds, sounds_json["interactive_entity_sounds"][entity_name], resource_pack_name)

        return Sorting.sort_everything(sounds_json)
