import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.DuplicateSounds.DuplicateSoundsDataMiner as DuplicateSoundsDataMiner
import DataMiners.DataMinerEnvironment as DataMinerEnvironment


class DuplicateSoundsDataMiner0(DuplicateSoundsDataMiner.DuplicateSoundsDataMiner):

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[str,list[DataMinerTyping.DuplicateSoundsTypedDict]]:
        sound_files = environment.dependency_data["sound_files"]
        assert sound_files is not None

        hash_dict:dict[str,list[DataMinerTyping.DuplicateSoundsTypedDict]] = {}
        for sound_file_name, sound_file_internals in sound_files.items():
            for sound_file_internal_name, sound_file_properties in sound_file_internals.items():
                if sound_file_properties["sha1_hash"] in hash_dict:
                    hash_dict[sound_file_properties["sha1_hash"]].append({"file_name": sound_file_name, "file_internal_name": sound_file_internal_name})
                else:
                    hash_dict[sound_file_properties["sha1_hash"]] = [{"file_name": sound_file_name, "file_internal_name": sound_file_internal_name}]

        return {sha1_hash: sorted(sounds, key=lambda value: (value["file_name"], value["file_internal_name"])) for sha1_hash, sounds in hash_dict.items() if len(sounds) > 1}
