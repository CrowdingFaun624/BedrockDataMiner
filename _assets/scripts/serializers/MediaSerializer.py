import json
import subprocess
from typing import Any, Iterator, Literal, TypedDict, cast

from typing_extensions import NotRequired, Required

import Component.Importer as Importer
import Serializer.Serializer as Serializer
import Utilities.CustomJson as CustomJson
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.FileManager as FileManager
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class OutputTypedDict(TypedDict):
    sha1_hash: Required[str]
    metadata: Required[File.File[dict[str,Any]]]
    unknown_file_type: NotRequired[File.File[Any]]
    CUR: NotRequired[File.File[Any]]
    GIF: NotRequired[File.File[Any]]
    JPEG: NotRequired[File.File[Any]]
    M4A: NotRequired[File.File[Any]]
    MP3: NotRequired[File.File[Any]]
    MP4: NotRequired[File.File[Any]]
    OTF: NotRequired[File.File[Any]]
    PNG: NotRequired[File.File[Any]]
    SVG: NotRequired[File.File[Any]]
    TTC: NotRequired[File.File[Any]]
    TTF: NotRequired[File.File[Any]]
    WEBM: NotRequired[File.File[Any]]

__all__ = ["MediaSerializer"]

class MediaSerializer(Serializer.Serializer):

    store_as_file_default = False

    empty_okay = True # 1.11.0.9 resource_packs/vanilla/textures/ui/book_arrowleft_hover.png

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("metadata_serializer_name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("file_serializer_names", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, str, "a dict", "a str", "a str")),
    )

    can_contain_subfiles = True

    def __init__(self, name: str, metadata_serializer_name:str, file_serializer_names:dict[str,str]) -> None:
        super().__init__(name)
        self.cached_data:dict[str,OutputTypedDict]|None = None
        self.metadata_serializer_name = metadata_serializer_name
        self.metadata_serializer:Serializer.Serializer|None = None
        self.file_serializer_names = file_serializer_names
        self.file_serializers:dict[str,Serializer.Serializer]|None = None

    def get_metadata_serializer(self) -> Serializer.Serializer:
        if self.metadata_serializer is None:
            self.metadata_serializer = Importer.serializers[self.metadata_serializer_name]
        return self.metadata_serializer

    def get_file_type_serializer(self, file_type:str) -> Serializer.Serializer:
        if self.file_serializers is None:
            self.file_serializers = {file_type: Importer.serializers[serializer_name] for file_type, serializer_name in self.file_serializer_names.items()}
        return self.file_serializers[file_type]

    def get_cache(self) -> dict[str,OutputTypedDict]:
        if self.cached_data is None:
            with open(FileManager.EXIFTOOL_CACHE, "rt") as f:
                self.cached_data = {line[:40]: json.loads(line[41:], cls=CustomJson.decoder) for line in f.readlines()}
        return self.cached_data

    def write_cache(self, sha1_hash:str, data:OutputTypedDict) -> None:
        assert len(sha1_hash) == 40
        cache = self.get_cache()
        assert sha1_hash not in cache
        cache[sha1_hash] = data
        with open(FileManager.EXIFTOOL_CACHE, "at") as f:
            f.write("%s %s\n" % (sha1_hash, json.dumps(data, separators=(",", ":"), cls=CustomJson.encoder)))

    def deserialize(self, data: bytes) -> OutputTypedDict:
        data_hash = FileManager.stringify_sha1_hash(FileManager.get_hash_bytes(data))
        cached_item = self.get_cache().get(data_hash)
        if cached_item is not None:
            return cached_item

        temp_file_path = FileManager.get_temp_file_path()
        with open(temp_file_path, "wb") as f:
            f.write(data)
        process = subprocess.Popen([FileManager.LIB_EXIFTOOL_EXE_FILE, temp_file_path, "-j", "-b"], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr is not None:
            print(stderr)
            raise subprocess.CalledProcessError(process.returncode, process.args, stdout, stderr)
        if process.stdout is None:
            raise Exceptions.AttributeNoneError("stdout", process)
        temp_file_path.unlink()

        exiftool_output:list[dict[str,Any]] = json.loads(stdout.decode())
        assert len(exiftool_output) == 1
        file_type:Literal["CUR", "GIF", "JPEG", "M4A", "MP3", "MP4", "OTF", "PNG", "SVG", "TTC", "TTF", "WEBM"] = exiftool_output[0].pop("FileType", "unknown_file_type")
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
            "metadata": File.new_file(json.dumps(metadata).encode(), "metadata_of_%s" % (data_hash,), self.get_metadata_serializer()),
        }
        output[file_type] = File.new_file(data, "media_%s" % (data_hash,), self.get_file_type_serializer(file_type))

        self.write_cache(data_hash, output)
        return output

    def get_referenced_files(self, data: bytes) -> Iterator[int]:
        data_hash = FileManager.stringify_sha1_hash(FileManager.get_hash_bytes(data))
        cached_item = self.get_cache().get(data_hash)
        if cached_item is not None:
            # if there is no cached data, there are no files stored at the moment
            # for this file. If some do exist, they would have to be
            # recalculated anyway, since they aren't in the cache
            yield cached_item["metadata"].hash # contains no subfiles
            for key, value in cached_item.items():
                if key in {"sha1_hash", "metadata"}: continue
                image_file = cast(File.File[Any], value)
                yield image_file.hash # contains no subfiles
