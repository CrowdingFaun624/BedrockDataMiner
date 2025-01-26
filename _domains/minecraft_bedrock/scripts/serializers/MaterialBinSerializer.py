import json
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, TypedDict

import Domain.Domain as Domain
import Domain.Domains as Domains
import Serializer.Serializer as Serializer
import Utilities.Cache as Cache
import Utilities.File as File
import Utilities.FileManager as FileManager
import Utilities.TypeVerifier as TypeVerifier

__all__ = ("MaterialBinSerializer",)

class PassTypedDict(TypedDict):
    pass_info: File.File[Any]
    glsl_files: dict[str,File.File[str]]

class OutputTypedDict(TypedDict):
    data: File.File[Any]
    passes: dict[str,PassTypedDict]

class MaterialBinCache(Cache.LinesCache[dict[str,dict[str,str]], tuple[str,str,str]]):

    def __init__(self, domain:Domain.Domain) -> None:
        domain.data_directory.mkdir(exist_ok=True)
        super().__init__(domain.data_directory.joinpath("material_bin_cache.txt"))

    def get_default_content(self) -> dict[str, dict[str, str]] | None:
        return defaultdict(lambda: {})

    def deserialize_line(self, line:str) -> dict[str,str]:
        return dict(zip(("version", "source_hash", "output"), line.split(" ", maxsplit=2), strict=True))

    def deserialize(self, data: bytes) -> dict[str,dict[str,str]]:
        contents = {(line_data := self.deserialize_line(line))["source_hash"]: (line_data["output"], line_data["version"]) for line in data.decode().splitlines()}
        output:defaultdict[str,dict[str,str]] = defaultdict(lambda: {})
        for source_hash, (line_output, version) in contents.items():
            output[version][source_hash] = line_output
        return output

    def serialize_line(self, data: tuple[str, str, str]) -> str:
        version, source_hash, output = data
        return f"{version} {source_hash} {output}\n"

    def append_new_line(self, data: tuple[str, str, str]) -> None:
        version, source_hash, output = data
        assert source_hash not in self.get()[version]
        self.get()[version][source_hash] = output

material_bin_cache = MaterialBinCache(Domains.get_domain_from_module(__name__))

class MaterialBinSerializer(Serializer.Serializer[OutputTypedDict,File.File[OutputTypedDict]]):

    store_as_file_default = True

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("version", True, str),
    )

    can_contain_subfiles = True

    linked_serializers = {key: Serializer.Serializer for key in ("data", "main", "pass_info", "glsl")}

    def __init__(self, name: str, domain:Domain.Domain, version:str) -> None:
        super().__init__(name, domain)
        # self.cached_data:dict[str,str]|None = None
        self.version = version
        assert not any(char in self.version for char in "\\/:*?\"<>|")

    def get_linked_serializers(self, linked_serializers: dict[str, Serializer.Serializer]) -> None:
        self.data_serializer = linked_serializers["data"]
        self.main_serializer = linked_serializers["main"]
        self.pass_info_serializer = linked_serializers["pass_info"]
        self.glsl_serializer = linked_serializers["glsl"]

    def write_cache(self, source_hash:str, output:OutputTypedDict) -> File.File[OutputTypedDict]:
        output_file = File.new_file(json.dumps(output, separators=(",", ":"), cls=self.domain.json_encoder).encode(), f"material_bin_data_of_{source_hash}", self.data_serializer)
        output_str = json.dumps(output_file, separators=(",", ":"), cls=self.domain.json_encoder)
        material_bin_cache.append_new_line((self.version, source_hash, output_str))
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
        jar_file = self.domain.lib_files[f"MaterialBinTool/MaterialBinTool-{self.version}-all.jar"]
        command = (
            "java",
            "-jar", jar_file,
            "-u", input_file,
            "-o", temporary_directory,
        )
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
        file_name = f"main_material_bin_of_{data_hash}.json"
        main_data_path = output_directory.joinpath("data.json")
        with open(main_data_path, "rb") as f:
            main_data_bytes = f.read()
            main_data_file = File.new_file(main_data_bytes, file_name, self.main_serializer)
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
                pass_info_file = File.new_file(f.read(), f"pass_info_in_{pass_name}_of_{data_hash}", self.pass_info_serializer)
            pass_info_path.unlink()
            glsl_files = self.get_glsl_files(pass_directory, data_hash)
            pass_directory.rmdir()
            passes[pass_name] = {"pass_info": pass_info_file, "glsl_files": glsl_files}
        return passes

    def get_glsl_files(self, pass_directory:Path, data_hash:str) -> dict[str,File.File[str]]:
        glsl_files:dict[str,File.File[str]] = {}
        for glsl_file_path in pass_directory.iterdir():
            with open(glsl_file_path, "rb") as f:
                glsl_file = File.new_file(f.read(), f"glsl_file_{glsl_file_path.name}_in_{pass_directory.name}_of_{data_hash}", self.glsl_serializer)
            glsl_file_path.unlink()
            glsl_files[glsl_file_path.name] = glsl_file
        return glsl_files

    def deserialize(self, data: bytes) -> File.File[OutputTypedDict]:
        data_hash = FileManager.get_hash_hexdigest(data)

        cached_output = material_bin_cache.get()[self.version].get(data_hash)
        if cached_output is not None:
            return json.loads(cached_output, cls=self.domain.json_decoder)

        temporary_directory = self.run_material_bin_tool(data)
        output_directory = temporary_directory.joinpath("data")

        main_data_file, pass_names = self.get_main_data_file(output_directory, data_hash)
        output:OutputTypedDict = {"data": main_data_file, "passes": self.get_pass_files(output_directory, pass_names, data_hash)}

        output_directory.rmdir()
        temporary_directory.rmdir()
        output_file = self.write_cache(data_hash, output)

        return output_file

    def get_referenced_files(self, data: bytes, referenced_files:set[int]) -> None:
        data_hash = FileManager.get_hash_hexdigest(data)
        cached_output = material_bin_cache.get()[self.version].get(data_hash)
        if cached_output is not None:
            # if it's not cached, there's no referenced files. If they do exist
            # in the file storage, they would have to be recalculated anyways.
            File.recursive_examine_data_for_files(json.loads(cached_output, cls=self.domain.json_decoder), referenced_files)
