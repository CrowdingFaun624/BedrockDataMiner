import audio_metadata
import enum
from typing import Any, IO

import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.FileManager as FileManager

ALL_SOUND_FILE_FORMATS = [".flac", ".fsb", ".mp3", ".ogg", ".wav"]

def get_metadata(file:FileManager.FilePromise) -> dict[str,Any]:
    with file.open() as file_io:
        if FileManager.get_file_size(file_io) == 0:
            raise ValueError("`file` refers to an IO with no bytes!")
        if not isinstance(file_io, IO): # If it's from a zip file or something, it can't be read by audio_metadata.
            temp_file = FileManager.get_temp_file_path()
            exception = None
            with open(temp_file, "wb") as temp_file_io:
                temp_file_io.write(file_io.read())
                file_io.seek(0)
            with open(temp_file, "rb") as temp_file_io:
                try:
                    metadata = audio_metadata.load(temp_file_io)
                    file_io.seek(0)
                except Exception as e:
                    exception = e
                if exception is not None:
                    print("audio_metadata failed to extract file \"%s\"!" % file.name)
                    raise exception
                info = serialize(metadata)
            temp_file.unlink()
        else:
            temp_file = None
            exception = None
            try:
                metadata = audio_metadata.load(file_io)
                file_io.seek(0)
            except Exception as e:
                exception = e
            if exception is not None:
                print("audio_metadata failed to extract file \"%s\"!" % file.name)
                raise exception
            info = serialize(metadata)
            
        del info["filepath"]
        sha1_hash = FileManager.stringify_sha1_hash(FileManager.get_hash(file_io))
        info["sha1_hash"] = sha1_hash
    file.all_done()
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
    elif type(data) == bytes:
        return hex(data)
    else:
        try:
            return serialize(dict(data))
        except Exception:
            return "Unencodable object \"%s\"" % data.__class__.__name__

class SoundFilesDataMiner(DataMiner.DataMiner):
    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> dict[str,dict[str,DataMinerTyping.SoundFilesTypedDict]]:
        return super().activate(dependency_data)
