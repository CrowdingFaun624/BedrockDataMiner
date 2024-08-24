import enum
from typing import Any, TypedDict

import Programs.EvilFSBExtractor as EvilFSBExtractor
import Serializer.Serializer as Serializer
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager


class SoundFilesTagsTypedDict(TypedDict):
    comment: list[str]
    title: list[str]
    tracknumber: list[str]

class SoundFilesStreamInfoTypedDict(TypedDict):
    _start: int
    _size: int
    _version: list[int]
    _extension_data: None
    audio_format: str
    bit_depth: int
    bitrate: float|int
    channels: int
    duration: float
    max_bitrate: int
    min_bitrate: int
    nominal_bitrate: int
    sample_rate: int

class SoundFilesTypedDict(TypedDict):
    filesize: int
    pictures: list
    tags: SoundFilesTagsTypedDict
    _subchunks: list
    _obj: str
    streaminfo: SoundFilesStreamInfoTypedDict
    sha1_hash: str # hexadecimal 40-digit string

ALL_SOUND_FILE_FORMATS = [".flac", ".fsb", ".mp3", ".ogg", ".wav"]

def get_metadata(file:bytes) -> SoundFilesTypedDict:
    import audio_metadata
    if len(file) == 0:
        raise Exceptions.EmptyFileError()
    try:
        metadata = audio_metadata.loads(file)
    except Exception as e:
        raise Exceptions.SoundFilesMetadataError()
    info = serialize(metadata)

    sha1_hash = FileManager.stringify_sha1_hash(FileManager.get_hash_bytes(file))
    info["sha1_hash"] = sha1_hash
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

class SoundSerializer(Serializer.Serializer[dict[str,dict[str,SoundFilesTypedDict]],dict[str,dict[str,SoundFilesTypedDict]]]):

    store_as_file_default = False

    def deserialize(self, data: bytes) -> dict[str,SoundFilesTypedDict]:
        if data[:3] == b"FSB": # it's an FSB file
            wav_files = EvilFSBExtractor.extract_fsb_file(data)
            output:dict[str,SoundFilesTypedDict] = {}
            for wav_file_name, wav_file_promise in wav_files.items():
                with wav_file_promise.open() as wav_file_data:
                    output[wav_file_name] = get_metadata(wav_file_data.read())
                wav_file_promise.all_done()
            return output
        else:
            return {"main": get_metadata(data)}
