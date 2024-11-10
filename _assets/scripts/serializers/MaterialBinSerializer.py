import json
import subprocess
from typing import Any, Iterator, TypedDict

from pathlib2 import Path

import Component.Importer as Importer
import Serializer.Serializer as Serializer
import Utilities.CustomJson as CustomJson
import Utilities.File as File
import Utilities.FileManager as FileManager
import Utilities.FileStorageManager as FileStorageManager
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["MaterialBinSerializer"]

class PassTypedDict(TypedDict):
    pass_info: File.File[Any]
    glsl_files: dict[str,File.File[str]]

class OutputTypedDict(TypedDict):
    data: File.File[Any]
    passes: dict[str,PassTypedDict]

class SerializerNamesTypedDict(TypedDict):
    data: str
    main: str
    pass_info: str
    glsl: str

class MaterialBinSerializer(Serializer.Serializer[OutputTypedDict,File.File[OutputTypedDict]]):

    store_as_file_default = True

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("version", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("subserializer_names", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("data", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("main", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("pass_info", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("glsl", "a str", True, str),
        )),
    )

    can_contain_subfiles = True

    def __init__(self, name: str, version:str, subserializer_names:SerializerNamesTypedDict) -> None:
        super().__init__(name)
        self.cached_data:dict[str,str]|None = None
        self.version = version
        assert not any(char in self.version for char in "\\/:*?\"<>|")
        self.data_serializer_name = subserializer_names["data"]
        self.data_serializer:Serializer.Serializer|None = None
        self.main_serializer_name = subserializer_names["main"]
        self.main_serializer:Serializer.Serializer|None = None
        self.pass_info_serializer_name = subserializer_names["pass_info"]
        self.pass_info_serializer:Serializer.Serializer|None = None
        self.glsl_serializer_name = subserializer_names["glsl"]
        self.glsl_serializer:Serializer.Serializer|None = None

    def get_data_serializer(self) -> Serializer.Serializer:
        if self.data_serializer is None:
            self.data_serializer = Importer.serializers[self.data_serializer_name]
        return self.data_serializer

    def get_main_serializer(self) -> Serializer.Serializer:
        if self.main_serializer is None:
            self.main_serializer = Importer.serializers[self.main_serializer_name]
        return self.main_serializer

    def get_pass_info_serializer(self) -> Serializer.Serializer:
        if self.pass_info_serializer is None:
            self.pass_info_serializer = Importer.serializers[self.pass_info_serializer_name]
        return self.pass_info_serializer

    def get_glsl_serializer(self) -> Serializer.Serializer:
        if self.glsl_serializer is None:
            self.glsl_serializer = Importer.serializers[self.glsl_serializer_name]
        return self.glsl_serializer

    def cache_parse_line(self, line:str) -> dict[str,str]:
        return dict(zip(("version", "source_hash", "output"), line.split(" ", maxsplit=2), strict=True))

    def get_cache(self) -> dict[str,str]:
        if self.cached_data is None:
            with open(FileManager.MATERIAL_BIN_CACHE_FILE, "rt") as f:
                self.cached_data = {line_data["source_hash"]: line_data["output"] for line in f.readlines() if (line_data := self.cache_parse_line(line))["version"] == self.version}
        return self.cached_data

    def write_cache(self, source_hash:str, output:OutputTypedDict) -> File.File[OutputTypedDict]:
        assert len(source_hash) == 40
        cache = self.get_cache()
        assert source_hash not in cache
        output_file = File.new_file(json.dumps(output, separators=(",", ":"), cls=CustomJson.encoder).encode(), "material_bin_data_of_%s" % (source_hash,), self.get_data_serializer())
        with open(FileManager.MATERIAL_BIN_CACHE_FILE, "at") as f:
            f.write("%s %s %s\n" % (self.version, source_hash, json.dumps(output_file, separators=(",", ":"), cls=CustomJson.encoder)))
        return output_file

    def run_material_bin_tool(self, data:bytes) -> Path:
        '''
        Returns temporary directory.
        '''
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
        with subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE) as process:
            process.wait()
            if process.returncode != 0:
                if process.stdout is not None:
                    print("STDOUT")
                    print(process.stdout.read().decode())
                if process.stderr is not None:
                    print("STDERR")
                    print(process.stderr.read().decode())
                raise subprocess.SubprocessError(command)
        input_file.unlink()
        return temporary_directory

    def get_main_data_file(self, output_directory:Path, data_hash:str) -> tuple[File.File[Any], list[str]]:
        '''
        Returns the main data file and the pass names contained within.
        '''
        file_name = "main_material_bin_of_%s.json" % (data_hash,)
        main_data_path = output_directory.joinpath("data.json")
        with open(main_data_path, "rb") as f:
            main_data_bytes = f.read()
            main_data_file = File.new_file(main_data_bytes, file_name, self.get_main_serializer())
        main_data = json.loads(main_data_bytes.decode())
        main_data_path.unlink()
        pass_names:list[str] = main_data["passes"]
        return main_data_file, pass_names

    def get_pass_files(self, output_directory:Path, pass_names:list[str], data_hash:str) -> dict[str,PassTypedDict]:
        passes:dict[str,PassTypedDict] = {}
        for pass_name in pass_names:
            pass_directory = output_directory.joinpath(pass_name)
            pass_info_path = pass_directory.joinpath(pass_name + ".json")
            with open(pass_info_path, "rb") as f:
                pass_info_file = File.new_file(f.read(), "pass_info_in_%s_of_%s" % (pass_name, data_hash), self.get_pass_info_serializer())
            pass_info_path.unlink()
            glsl_files = self.get_glsl_files(pass_directory, data_hash)
            pass_directory.rmdir()
            passes[pass_name] = {"pass_info": pass_info_file, "glsl_files": glsl_files}
        return passes

    def get_glsl_files(self, pass_directory:Path, data_hash:str) -> dict[str,File.File[str]]:
        glsl_files:dict[str,File.File[str]] = {}
        for glsl_file_path in pass_directory.iterdir():
            with open(glsl_file_path, "rb") as f:
                glsl_file = File.new_file(f.read(), "glsl_file_%s_in_%s_of_%s" % (glsl_file_path.name, pass_directory.name, data_hash), self.get_glsl_serializer())
            glsl_file_path.unlink()
            glsl_files[glsl_file_path.name] = glsl_file
        return glsl_files

    def deserialize(self, data: bytes) -> File.File[OutputTypedDict]:
        data_hash = FileManager.stringify_sha1_hash(FileManager.get_hash_bytes(data))

        cached_output = self.get_cache().get(data_hash)
        if cached_output is not None:
            return json.loads(cached_output, cls=CustomJson.decoder)

        temporary_directory = self.run_material_bin_tool(data)
        output_directory = temporary_directory.joinpath("data")

        main_data_file, pass_names = self.get_main_data_file(output_directory, data_hash)
        output:OutputTypedDict = {"data": main_data_file, "passes": self.get_pass_files(output_directory, pass_names, data_hash)}

        output_directory.rmdir()
        temporary_directory.rmdir()
        output_file = self.write_cache(data_hash, output)

        return output_file

    def get_referenced_files(self, data: bytes) -> Iterator[int]:
        data_hash = FileManager.stringify_sha1_hash(FileManager.get_hash_bytes(data))
        cached_output = self.get_cache().get(data_hash)
        if cached_output is not None:
            # if it's not cached, there's no referenced files. If they do exist
            # in the file storage, they would have to be recalculated anyways.
            yield from File.recursive_examine_data_for_files(json.loads(cached_output, cls=CustomJson.decoder))
