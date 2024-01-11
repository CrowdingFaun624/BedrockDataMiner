import DataMiners.SoundFiles.SoundFilesDataMiner as SoundFilesDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Programs.EvilFSBExtractor as EvilFSBExtractor


class SoundFilesDataMiner0(SoundFilesDataMiner.SoundFilesDataMiner):
    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> dict[str,dict[str,DataMinerTyping.SoundFilesTypedDict]]:
        file_list = self.get_file_list()
        assert not any("\\" in file for file in file_list) # can't trust it, you see.
        if len(file_list) == 0:
            raise FileNotFoundError("No files found for `sound_files` in version \"%s\"!" % self.version.name)
        
        output:dict[str,dict[str,DataMinerTyping.SoundFilesTypedDict]] = {}
        for file_path in file_list:
            if "." + file_path.split(".")[-1].lower() in SoundFilesDataMiner.ALL_SOUND_FILE_FORMATS and not file_path.endswith(".fsb"):
                output[file_path] = {"main": SoundFilesDataMiner.get_metadata(self.get_file(file_path, "b"))}

        fsb_file_names:dict[str,str] = (name for name in file_list if name.lower().endswith(".fsb"))
        fsb_files = EvilFSBExtractor.extract_fsb_files((file_name, self.get_file(file_name, "b")) for file_name in fsb_file_names)
        for file_name, wav_files in fsb_files:
            output[file_name] = {}
            for wav_file_name, wav_file_promise in wav_files.items():
                output[file_name][wav_file_name] = SoundFilesDataMiner.get_metadata(wav_file_promise)
        
        output = {key: value for key, value in sorted(list(output.items()))}
        return output
