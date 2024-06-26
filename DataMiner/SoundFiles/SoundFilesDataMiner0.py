import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import DataMiner.SoundFiles.SoundFilesDataMiner as SoundFilesDataMiner
import Programs.EvilFSBExtractor as EvilFSBExtractor
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting


class SoundFilesDataMiner0(SoundFilesDataMiner.SoundFilesDataMiner):

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[str,dict[str,DataMinerTyping.SoundFilesTypedDict]]:
        accessor = self.get_accessor("client")
        file_list = accessor.get_file_list()
        if len(file_list) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        output:dict[str,dict[str,DataMinerTyping.SoundFilesTypedDict]] = {}
        for file_path in file_list:
            if "." + file_path.split(".")[-1].lower() in SoundFilesDataMiner.ALL_SOUND_FILE_FORMATS and not file_path.endswith(".fsb"):
                output[file_path] = {"main": SoundFilesDataMiner.get_metadata(accessor.get_file(file_path, "b"))}

        fsb_file_names = (name for name in file_list if name.lower().endswith(".fsb"))
        fsb_files = EvilFSBExtractor.extract_fsb_files((file_name, accessor.get_file(file_name, "b")) for file_name in fsb_file_names)
        for file_name, wav_files in fsb_files:
            output[file_name] = {}
            for wav_file_name, wav_file_promise in wav_files.items():
                output[file_name][wav_file_name] = SoundFilesDataMiner.get_metadata(wav_file_promise)

        return Sorting.sort_everything(output)
