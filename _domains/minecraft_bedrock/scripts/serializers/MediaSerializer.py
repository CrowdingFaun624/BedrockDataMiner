import json
import subprocess
from typing import (Any, Iterator, Literal, NotRequired, Required, TypedDict,
                    cast)

import Domain.Domain as Domain
import Domain.Domains as Domains
import Serializer.Serializer as Serializer
import Utilities.Cache as Cache
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.FileManager as FileManager


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

class MediaSerializerCache(Cache.LinesCache[dict[str,OutputTypedDict], tuple[str, OutputTypedDict]]):

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

media_serializer_cache = MediaSerializerCache(Domains.get_domain_from_module(__name__))

class MediaSerializer(Serializer.Serializer):

    store_as_file_default = False

    empty_okay = False

    can_contain_subfiles = True

    linked_serializers = {key: Serializer.Serializer for key in ("metadata", "file_unknown", "file_CUR", "file_GIF", "file_JPEG", "file_M4A", "file_MP3", "file_MP4", "file_OTF", "file_PNG", "file_SVG", "file_TTC", "file_TTF", "file_WEBM")}

    def __init__(self, name: str, domain:Domain.Domain) -> None:
        super().__init__(name, domain)
        self.cached_data:dict[str,OutputTypedDict]|None = None

    def get_linked_serializers(self, linked_serializers: dict[str, Serializer.Serializer]) -> None:
        self.metadata_serializer = linked_serializers["metadata"]
        self.file_serializers = {key.replace("file_", ""): serializer for key, serializer in linked_serializers.items() if key.startswith("file_")}

    def deserialize(self, data: bytes) -> OutputTypedDict:
        data_hash = FileManager.get_hash_hexdigest(data)
        cached_item = media_serializer_cache.get().get(data_hash)
        if cached_item is not None:
            return cached_item

        temp_file_path = FileManager.get_temp_file_path()
        with open(temp_file_path, "wb") as f:
            f.write(data)
        process = subprocess.Popen([self.domain.lib_files["exiftool-12.93_64/exiftool.exe"], temp_file_path, "-j", "-b"], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr is not None:
            print(stderr)
            raise subprocess.CalledProcessError(process.returncode, process.args, stdout, stderr)
        if process.stdout is None:
            raise Exceptions.AttributeNoneError("stdout", process)
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
            "metadata": File.new_file(json.dumps(metadata).encode(), f"metadata_of_{data_hash}.json", self.metadata_serializer),
        }
        output[file_type] = File.new_file(data, f"media_{data_hash}.{file_type}", self.file_serializers[file_type])

        media_serializer_cache.write_new_line((data_hash, output))
        return output

    def get_referenced_files(self, data: bytes) -> Iterator[int]:
        data_hash = FileManager.get_hash_hexdigest(data)
        cached_item = media_serializer_cache.get().get(data_hash)
        if cached_item is not None:
            # if there is no cached data, there are no files stored at the moment
            # for this file. If some do exist, they would have to be
            # recalculated anyway, since they aren't in the cache
            yield cached_item["metadata"].hash # contains no subfiles
            for key, value in cached_item.items():
                if key in {"sha1_hash", "metadata"}: continue
                image_file = cast(File.File[Any], value)
                yield image_file.hash # contains no subfiles
