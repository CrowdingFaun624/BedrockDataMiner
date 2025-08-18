import subprocess
import zipfile
from pathlib import Path
from typing import BinaryIO, Literal, TypedDict

from _domains.minecraft_common.scripts.accessors.ArchivalAccessor import (
    ArchivalAccessor,
)
from Component.ComponentFunctions import component_function
from Domain.Domain import Domain
from Downloader.Accessor import Accessor
from Downloader.FileAccessor import FileAccessor
from Downloader.ZipAccessor import ZipAccessor
from Utilities.FileManager import get_temp_file_path
from Utilities.TypeVerifier import (
    EnumTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)
from Version.Version import Version


class InstanceArguments(TypedDict):
    method: Literal[0, 1]

class ClassArguments(TypedDict):
    java_location: str

@component_function()
class DataGeneratorAccessor(FileAccessor):
    """
    Downloads files from the internet and runs them. What could go wrong?????
    """

    __slots__ = (
        "installed",
        "java_location",
        "method",
        "temp_path",
        "zip_location",
    )

    class_parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("java_location", True, str),
    )

    instance_parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("method", True, EnumTypeVerifier({0, 1}))
    )

    def __init__(self, full_name: str, version: Version, domain: Domain, instance_arguments: InstanceArguments, class_arguments: ClassArguments, linked_accessors: dict[str, Accessor]) -> None:
        super().__init__(full_name, version, domain, instance_arguments, class_arguments, linked_accessors)
        self.method = instance_arguments["method"]
        self.java_location = class_arguments["java_location"]
        self.installed = False
        self.temp_path:Path
        self.zip_location:Path

    def install(self) -> None:
        server_accessor = self.version.version_files_dict["server"].get_accessor(ZipAccessor).linked_accessors["file"]
        assert isinstance(server_accessor, ArchivalAccessor)
        server_accessor.store()
        server_location = server_accessor.archive_location

        temp_path = get_temp_file_path()
        temp_path.mkdir()
        output_location = temp_path.joinpath("generated")
        output_location.mkdir()
        eula_file = Path("eula.txt") # required for some 1.13 snapshots (btw this file is in the base directory; I am sorry.)
        assert not eula_file.exists() # hopefully I never make a eula file at this exact spot
        with open(eula_file, "wt") as f:
            f.write("eula=true")
        if self.method == 1:
            command = (self.java_location, "-DbundlerMainClass=net.minecraft.data.Main", "-jar", server_location, "--reports", "--output", output_location)
        elif self.method == 0:
            command = (self.java_location, "-cp", server_location, "net.minecraft.data.Main", "--reports", "--output", output_location)
        else:
            raise RuntimeError(f"Invalid method: {self.method}")
        process = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr is not None:
            eula_file.unlink()
            print(stderr.decode())
            raise subprocess.CalledProcessError(process.returncode, process.args, stdout, stderr)
        # elif b"Exception" in stdout or b"Error" in stdout:
        #     print(stdout.decode())
        #     eula_file.unlink()
        #     raise subprocess.CalledProcessError(process.returncode, process.args, stdout, stderr)

        # zip the output created by the server, deleting the files as they are consumed.
        zip_location = temp_path.joinpath("output.zip")
        file_count:int = 0
        all_files:list[Path] = [output_location]
        eula_file.unlink()
        with zipfile.ZipFile(zip_location, "w", zipfile.ZIP_DEFLATED) as f:
            for output_file in output_location.rglob("*"):
                all_files.append(output_file)
                if not output_file.is_file(): continue
                relative_name = output_file.relative_to(output_location).as_posix()
                file_count += not relative_name.startswith(".cache")
                with open(output_file, "rb") as subfile:
                    f.writestr(relative_name, subfile.read())
        all_files.reverse()
        for file in all_files:
            if file.is_file(): file.unlink()
            elif file.is_dir(): file.rmdir()
        if file_count == 0:
            if stdout is not None:
                print(stdout.decode())
            raise FileNotFoundError("No files found in generated data report!")
        self.installed = True
        self.temp_path = temp_path
        self.zip_location = zip_location

    def open(self) -> BinaryIO:
        if not self.installed:
            self.install()
        return open(self.zip_location, "rb")

    def close(self) -> None:
        super().close()
        if self.installed:
            self.installed = False
            self.zip_location.unlink()
            self.temp_path.rmdir()

    def all_done(self) -> None:
        self.close()
        super().all_done()
