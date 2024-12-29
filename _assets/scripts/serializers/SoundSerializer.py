import enum
from typing import Any, Iterator, Optional, TypedDict

import _assets.scripts.serializers.EvilFSBExtractor as EvilFSBExtractor
import Serializer.Serializer as Serializer
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.FileManager as FileManager

__all__ = ["SoundSerializer"]

class SoundFilesMetadataError(Exceptions.DataMinerException):
    "audio_metadata failed to extract the sound file."

    def __init__(self, message:Optional[str]=None) -> None:
        '''
        :message: Additional text to place after the main message.'''
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"audio_metadata failed to extract a file{Exceptions.message(self.message)}"

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
        raise SoundFilesMetadataError()
    info = serialize(metadata)

    info["sha1_hash"] = FileManager.get_hash_hexdigest(file)
    return info

def serialize(data:Any) -> Any:
    if type(data) in (str, int, bool, type(None), float):
        return data
    elif type(data) in (list, tuple):
        return [serialize(item) for item in data]
    elif type(data) == dict:
        return {key: serialize(value) for key, value in data.items()}
    elif isinstance(data, enum.Enum):
        # audio_metadata changed one of its enums, thus changing all future
        # comparisons. This change is to undo that.
        return f"{data.__class__.__name__}.{data.name}"
    elif type(data) == bytes:
        return hex(int.from_bytes(data, "big"))
    else:
        try:
            return serialize(dict(data))
        except Exception:
            return f"Unencodable object \"{data.__class__.__name__}\""

class SoundSerializer(Serializer.Serializer[dict[str,dict[str,SoundFilesTypedDict]],dict[str,dict[str,SoundFilesTypedDict]]]):

    store_as_file_default = False

    can_contain_subfiles = True

    def deserialize(self, data: bytes) -> dict[str,SoundFilesTypedDict]:
        if data[:3] == b"FSB": # it's an FSB file
            wav_files = EvilFSBExtractor.extract_fsb_file(data)
            return {wav_file_name: get_metadata(wave_file_data) for wav_file_name, wave_file_data in wav_files}
        else:
            return {"main": get_metadata(data)}

    def get_referenced_files(self, data: bytes) -> Iterator[int]:
        if data[:3] == b"FSB":
            # this isn't *that* slow because it's cached.
            yield from (
                FileManager.get_hash_int(wav_file_data)
                for wav_file_name, wav_file_data in EvilFSBExtractor.extract_fsb_file(data)
            )
        else:
            yield FileManager.get_hash_int(data)
