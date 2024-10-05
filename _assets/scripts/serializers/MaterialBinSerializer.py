import json
import re
import subprocess
from typing import Any, TypedDict

import Serializer.JsonSerializer as JsonSerializer
import Serializer.Serializer as Serializer
import Utilities.File as File
import Utilities.FileManager as FileManager
import Utilities.FileStorageManager as FileStorageManager
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["MaterialBinSerializer"]

class PassTypedDict(TypedDict):
    pass_info: Any
    glsl_files: dict[str,str]

class OutputTypedDict(TypedDict):
    data: Any
    passes: dict[str,PassTypedDict]

version_pattern = re.compile(r"")

class MaterialBinSerializer(Serializer.Serializer[OutputTypedDict,File.File[OutputTypedDict]]):

    store_as_file_default = False # The source and output of this thing are huge
    # which is why this thing returns a file.

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("version", "a str", True, str),
    )

    def __init__(self, name: str, version:str) -> None:
        super().__init__(name)
        self.cached_data:dict[str,str]|None = None
        self.version = version
        assert not any(char in self.version for char in "\\/:*?\"<>|")

    def get_cache(self) -> dict[str,str]:
        if self.cached_data is None:
            with open(FileManager.MATERIAL_BIN_CACHE_FILE, "rt") as f:
                self.cached_data = {line[0:40]: line[40:80] for line in f.readlines()}
        return self.cached_data

    def write_cache(self, source_hash:str, destination_hash:str) -> None:
        assert len(source_hash) == 40
        cache = self.get_cache()
        assert source_hash not in cache
        cache[source_hash] = destination_hash
        with open(FileManager.MATERIAL_BIN_CACHE_FILE, "at") as f:
            f.write("%s%s\n" % (source_hash, destination_hash))

    def deserialize_json(self, data: File.File[OutputTypedDict]) -> OutputTypedDict:
        return data.data

    def deserialize(self, data: bytes) -> Any:
        data_hash = FileManager.stringify_sha1_hash(FileManager.get_hash_bytes(data))
        
        destination_hash = self.get_cache().get(data_hash)
        if destination_hash is not None:
            return File.File("cached_%s" % (data_hash,), JsonSerializer.DEFAULT_JSON_SERIALIZER, File.hash_str_to_int(destination_hash))
        
        temporary_directory = FileManager.get_temp_file_path()
        temporary_directory.mkdir()
        input_file = temporary_directory.joinpath("data.material.bin")
        with open(input_file, "wb") as f:
            f.write(data)

        jar_directory = FileManager.LIB_MATERIAL_BIN_TOOL_DIRECTORY.joinpath("MaterialBinTool-%s-all.jar" % (self.version,))
        command = [
            "java",
            "-jar", jar_directory,
            "-u", input_file,
            "-o", temporary_directory,
        ]
        subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        input_file.unlink()

        output_directory = temporary_directory.joinpath("data")
        main_data_file = output_directory.joinpath("data.json")
        with open(main_data_file, "rt") as f:
            main_data = json.load(f)
        main_data_file.unlink()
        pass_names:list[str] = main_data["passes"]
        output:OutputTypedDict = {"data": main_data, "passes": {}}

        for pass_name in pass_names:
            pass_directory = output_directory.joinpath(pass_name)
            pass_info_file = pass_directory.joinpath(pass_name + ".json")
            with open(pass_info_file, "rt") as f:
                pass_info = json.load(f)
            pass_info_file.unlink()

            glsl_files:dict[str,str] = {}
            for glsl_file_path in pass_directory.iterdir():
                with open(glsl_file_path, "rt") as f:
                    glsl_file = f.read()
                glsl_file_path.unlink()
                glsl_files[glsl_file_path.name] = glsl_file
            pass_directory.rmdir()

            output["passes"][pass_name] = {"pass_info": pass_info, "glsl_files": glsl_files}

        output_directory.rmdir()
        temporary_directory.rmdir()
        
        destination_hash = FileStorageManager.archive_data(json.dumps(output, separators=(",", ":")).encode(), "")
        self.write_cache(data_hash, destination_hash)

        return File.File("cached_%s" % (data_hash,), JsonSerializer.DEFAULT_JSON_SERIALIZER, File.hash_str_to_int(destination_hash))
