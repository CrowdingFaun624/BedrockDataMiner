import json
import subprocess
from typing import Any, Literal, NotRequired, Required, TypedDict

import Domain.Domain as Domain
from Domain.Domains import get_domain_from_module
from Serializer.Serializer import Serializer
from Utilities.Cache import LinesCache
from Utilities.Exceptions import AttributeNoneError
from Utilities.File import File, new_file
from Utilities.FileManager import get_hash_hexdigest, get_temp_file_path


class OutputTypedDict(TypedDict):
    sha1_hash: Required[str]
    metadata: Required[File[dict[str,Any]]]
    unknown_file_type: NotRequired[File[Any]]
    CUR: NotRequired[File[Any]]
    GIF: NotRequired[File[Any]]
    JPEG: NotRequired[File[Any]]
    M4A: NotRequired[File[Any]]
    MP3: NotRequired[File[Any]]
    MP4: NotRequired[File[Any]]
    OTF: NotRequired[File[Any]]
    PNG: NotRequired[File[Any]]
    SVG: NotRequired[File[Any]]
    TTC: NotRequired[File[Any]]
    TTF: NotRequired[File[Any]]
    WEBM: NotRequired[File[Any]]

__all__ = ("MediaSerializer",)

class MediaSerializerCache(LinesCache[dict[str,OutputTypedDict], tuple[str, OutputTypedDict]]):

    def __init__(self, domain:Domain.Domain) -> None:
        domain.data_directory.mkdir(exist_ok=True)
        super().__init__(domain.data_directory.joinpath("exiftool_cache.txt"))
        self.domain = domain

    def deserialize(self, data:bytes) -> dict[str,OutputTypedDict]:
        return {line[:40]: json.loads(line[41:], cls=self.domain.json_decoder) for line in data.decode("UTF8").splitlines()}

    def append_new_line(self, data: tuple[str, OutputTypedDict]) -> None:
        sha1_hash, file_data = data
        assert len(sha1_hash) == 40
        assert sha1_hash not in self.get()
        self.get()[sha1_hash] = file_data

    def serialize_line(self, data: tuple[str, OutputTypedDict]) -> str:
        sha1_hash, file_data = data
        return f"{sha1_hash} {json.dumps(file_data, separators=(",", ":"), cls=self.domain.json_encoder)}\n"

media_serializer_cache = MediaSerializerCache(get_domain_from_module(__name__))

class MediaSerializer(Serializer):

    empty_okay = False

    can_contain_subfiles = True

    def __init__(self, name: str, domain:Domain.Domain) -> None:
        super().__init__(name, domain)
        self.cached_data:dict[str,OutputTypedDict]|None = None

    def deserialize(self, data: bytes) -> OutputTypedDict:
        data_hash = get_hash_hexdigest(data)
        cached_item = media_serializer_cache.get().get(data_hash)
        if cached_item is not None:
            return cached_item

        temp_file_path = get_temp_file_path()
        with open(temp_file_path, "wb") as f:
            f.write(data)
        process = subprocess.Popen((self.domain.lib_files["exiftool-12.93_64/exiftool.exe"], temp_file_path, "-j", "-b"), stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr is not None:
            print(stderr)
            raise subprocess.CalledProcessError(process.returncode, process.args, stdout, stderr)
        if process.stdout is None:
            raise AttributeNoneError("stdout", process)
        temp_file_path.unlink()

        exiftool_output:list[dict[str,Any]] = json.loads(stdout.decode())
        assert len(exiftool_output) == 1
        file_type:Literal["CUR", "GIF", "JPEG", "M4A", "MP3", "MP4", "OTF", "PNG", "SVG", "TTC", "TTF", "WEBM"] = exiftool_output[0].pop("FileType", "unknown")
        metadata = exiftool_output[0]
        metadata.pop("ExifToolVersion", None)
        metadata.pop("SourceFile", None)
        metadata.pop("FileName", None)
        metadata.pop("Directory", None)
        metadata.pop("FileModifyDate", None)
        metadata.pop("FileAccessDate", None)
        metadata.pop("FileCreateDate", None)
        metadata.pop("FilePermissions", None)
        output:OutputTypedDict = {
            "sha1_hash": data_hash,
            "metadata": new_file(json.dumps(metadata).encode(), f"metadata_of_{data_hash}.json"),
        }
        output[file_type] = new_file(data, f"media_{data_hash}.{file_type}")

        media_serializer_cache.write_new_line((data_hash, output))
        return output
