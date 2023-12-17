import fsb5
from pathlib2 import Path

import DataMiners.SoundFiles.SoundFilesDataMiner as SoundFilesDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.FileManager as FileManager

class ArtificialSample():
    def __init__(self, name, frequency, channels, dataOffset, samples, metadata, data) -> None:
        self.name = name
        self.frequency = frequency
        self.channels = channels
        self.dataOffset = dataOffset
        self.samples = samples
        self.metadata = metadata
        self.data = data

class SoundFilesDataMiner0(SoundFilesDataMiner.SoundFilesDataMiner):
    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict|None=None) -> dict[str,dict[str,DataMinerTyping.SoundFilesTypedDict]]:
        file_list = self.get_file_list()
        for file_name in file_list:
            if not file_name.endswith(".fsb"): continue
            print(file_name)
            file = self.read_file(file_name, "b")
            sound_file = fsb5.load(file)
            header_list = list(sound_file.header) # Evil hack
            header_list[6] = fsb5.SoundFormat.VORBIS
            sound_file.header = fsb5.FSB5Header(*header_list)
            reconstructed_file = sound_file.rebuild_sample(sound_file.samples[0])

            print(reconstructed_file)
            destination_path = Path(FileManager.TEMP_FOLDER.joinpath("evil_sound_file.wav"))
            with open(destination_path, "wb") as f:
                f.write(reconstructed_file)

            assert False
