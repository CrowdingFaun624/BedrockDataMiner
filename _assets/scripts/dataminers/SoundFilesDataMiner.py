import enum
from typing import IO, Any

import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import Programs.EvilFSBExtractor as EvilFSBExtractor
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.Sorting as Sorting

__all__ = ["SoundFilesDataMiner"]

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
        accessor = self.get_accessor("client")
        file_list = accessor.get_file_list()
        if len(file_list) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        output:dict[str,dict[str,DataMinerTyping.SoundFilesTypedDict]] = {}
        for file_path in file_list:
            if "." + file_path.split(".")[-1].lower() in ALL_SOUND_FILE_FORMATS and not file_path.endswith(".fsb"):
                output[file_path] = {"main": get_metadata(accessor.get_file(file_path, "b"))}

        fsb_file_names = (name for name in file_list if name.lower().endswith(".fsb"))
        fsb_files = EvilFSBExtractor.extract_fsb_files((file_name, accessor.get_file(file_name, "b")) for file_name in fsb_file_names)
        for file_name, wav_files in fsb_files:
            output[file_name] = {}
            for wav_file_name, wav_file_promise in wav_files.items():
                output[file_name][wav_file_name] = get_metadata(wav_file_promise)

        return Sorting.sort_everything(output)
