import enum
from typing import IO, Any

import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager

ALL_SOUND_FILE_FORMATS = [".flac", ".fsb", ".mp3", ".ogg", ".wav"]

def get_metadata(file:FileManager.FilePromise) -> DataMinerTyping.SoundFilesTypedDict:
    import audio_metadata
    with file.open() as file_io:
        if FileManager.get_file_size(file_io) == 0:
            raise Exceptions.EmptyFileError(file)
        if not isinstance(file_io, IO): # If it's from a zip file or something, it can't be read by audio_metadata.
            temp_file = FileManager.get_temp_file_path()
            with open(temp_file, "wb") as temp_file_io:
                temp_file_io.write(file_io.read())
                file_io.seek(0)
            with open(temp_file, "rb") as temp_file_io:
                try:
                    metadata = audio_metadata.load(temp_file_io)
                    file_io.seek(0)
                except Exception as e:
                    raise Exceptions.SoundFilesMetadataError(file)
                info = serialize(metadata)
            temp_file.unlink()
        else:
            temp_file = None
            exception = None
            try:
                metadata = audio_metadata.load(file_io)
                file_io.seek(0)
            except Exception as e:
                raise Exceptions.SoundFilesMetadataError(file)
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
        return hex(int.from_bytes(data, "big"))
    else:
        try:
            return serialize(dict(data))
        except Exception:
            return "Unencodable object \"%s\"" % data.__class__.__name__

class SoundFilesDataMiner(DataMiner.DataMiner):

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[str,dict[str,DataMinerTyping.SoundFilesTypedDict]]:
        return super().activate(environment)
