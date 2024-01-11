import audio_metadata
import enum
from typing import Any, IO

import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.FileManager as FileManager
import Utilities.FileStorageManager as FileStorageManager

ALL_SOUND_FILE_FORMATS = [".flac", ".fsb", ".mp3", ".ogg", ".wav"]

def get_metadata(file:FileManager.FilePromise) -> dict[str,Any]:
    file_io = file.open()
    if not isinstance(file_io, IO): # If it's from a zip file or something, it can't be read.
        temp_file = FileManager.get_temp_file_path()
        with open(temp_file, "wb") as temp_file_io, file_io:
            temp_file_io.write(file_io.read())
        with open(temp_file, "rb") as temp_file_io:
            info = serialize(audio_metadata.load(temp_file_io))
    else:
        temp_file = None
        info = serialize(audio_metadata.load(file_io))
    del info["filepath"]
    sha1_hash = FileStorageManager.archive(file)
    info["sha1_hash"] = sha1_hash
    file.all_done()
    if temp_file is not None:
        temp_file.unlink()
    return info

def serialize(data:Any) -> Any:
    if type(data) in (str, int, bool, type(None), float):
        return data
    elif type(data) in (list, tuple):
        return [serialize(item) for item in data]
    elif type(data) == dict:
        return {key: serialize(value) for key, value in data.items()}
    elif isinstance(data, enum.Enum):
        return str(data)
    else:
        try:
            return serialize(dict(data))
        except Exception:
            return "Unencodable object \"%s\"" % data.__class__.__name__

class SoundFilesDataMiner(DataMiner.DataMiner):
    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> dict[str,dict[str,DataMinerTyping.SoundFilesTypedDict]]:
        return super().activate(dependency_data)
