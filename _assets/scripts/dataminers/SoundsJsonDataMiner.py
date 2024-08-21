import _assets.scripts.dataminers.GrabPackFileDataMiner as GrabPackFileDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import _assets.scripts.dataminers.DataMinerTyping as DataMinerTyping
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["SoundsJsonDataMiner"]

class SoundsJsonDataMiner(GrabPackFileDataMiner.GrabPackFileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("locations", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
    )

    def initialize(self, locations:list[str]) -> None:
        super().initialize(locations, "resource_packs")

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

    def get_output(self, files: dict[str,DataMinerTyping.SoundsJsonTypedDict], pack_files: dict[str, str], environment: DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.MySoundsJsonTypedDict:
        output:DataMinerTyping.MySoundsJsonTypedDict = {
            "individual_event_sounds": {},
            "block_sounds": {},
            "interactive_block_sounds": {},
            "entity_sounds": {},
            "interactive_entity_sounds": {},
        }
        for file_name, sounds_json in files.items():
            pack_name = pack_files[file_name]

            # individual_event_sounds
            if "individual_event_sounds" in sounds_json:
                self.parse_flat_sound_collection(sounds_json["individual_event_sounds"], output["individual_event_sounds"], pack_name)

            # block_sounds
            if "block_sounds" in sounds_json:
                for block_sound_type_name, block_sound_type_properties in sounds_json["block_sounds"].items():
                    if block_sound_type_name not in output["block_sounds"]:
                        output["block_sounds"][block_sound_type_name] = {}
                    self.parse_sound_collection(block_sound_type_properties, output["block_sounds"][block_sound_type_name], pack_name)

            # interactive_block_sounds
            if "interactive_sounds" in sounds_json and "block_sounds" in sounds_json["interactive_sounds"]:
                for block_sound_type_name, block_sound_type_properties in sounds_json["interactive_sounds"]["block_sounds"].items():
                    if block_sound_type_name not in output["interactive_block_sounds"]:
                        output["interactive_block_sounds"][block_sound_type_name] = {}
                    self.parse_sound_collection(block_sound_type_properties, output["interactive_block_sounds"][block_sound_type_name], pack_name)

            # entity_sounds
            if "entity_sounds" in sounds_json:
                if "defaults" in sounds_json["entity_sounds"]:
                    if "defaults" not in output["entity_sounds"]:
                        output["entity_sounds"]["defaults"] = {}
                    self.parse_sound_collection(sounds_json["entity_sounds"]["defaults"], output["entity_sounds"]["defaults"], pack_name)
                if "entities" in sounds_json["entity_sounds"]:
                    for entity_name, entity_sounds in sounds_json["entity_sounds"]["entities"].items():
                        if entity_name == "defaults": raise Exceptions.DataMinerFailureError(self, "An entity named \"defaults\" clashes with the separate defaults object in %s!" % (pack_name,))
                        if entity_name not in output["entity_sounds"]:
                            output["entity_sounds"][entity_name] = {}
                        self.parse_sound_collection(entity_sounds, output["entity_sounds"][entity_name], pack_name)

            # interactive_entity_sounds
            if "interactive_sounds" in sounds_json and "entity_sounds" in sounds_json["interactive_sounds"]:
                if "defaults" in sounds_json["interactive_sounds"]["entity_sounds"]:
                    if "defaults" not in output["interactive_entity_sounds"]:
                        output["interactive_entity_sounds"]["defaults"] = {}
                    self.parse_sound_collection(sounds_json["interactive_sounds"]["entity_sounds"]["defaults"], output["entity_sounds"]["defaults"], pack_name)
                if "entities" in sounds_json["interactive_sounds"]["entity_sounds"]:
                    for entity_name, entity_sounds in sounds_json["interactive_sounds"]["entity_sounds"]["entities"].items():
                        if entity_name == "defaults": raise Exceptions.DataMinerFailureError(self, "An interactive entity named \"defaults\" clashes withe the separate defaults object in %s!" % (pack_name))
                        if entity_name not in output["interactive_entity_sounds"]:
                            output["interactive_entity_sounds"][entity_name] = {}
                        self.parse_sound_collection(entity_sounds, output["interactive_entity_sounds"][entity_name], pack_name)
        return output
