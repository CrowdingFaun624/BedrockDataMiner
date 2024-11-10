import json
import subprocess

import Serializer.Serializer as Serializer
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager


class MediaSerializer(Serializer.Serializer):

    store_as_file_default = False

    empty_okay = True # 1.11.0.9 resource_packs/vanilla/textures/ui/book_arrowleft_hover.png

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.cached_data:dict[str,dict[str,str]]|None = None

    def get_cache(self) -> dict[str,dict[str,str]]:
        if self.cached_data is None:
            with open(FileManager.EXIFTOOL_CACHE, "rt") as f:
                self.cached_data = {line[:40]: json.loads(line[41:]) for line in f.readlines()}
        return self.cached_data

    def write_cache(self, sha1_hash:str, data:dict[str,str]) -> None:
        assert len(sha1_hash) == 40
        cache = self.get_cache()
        assert sha1_hash not in cache
        cache[sha1_hash] = data
        with open(FileManager.EXIFTOOL_CACHE, "at") as f:
            f.write("%s %s\n" % (sha1_hash, json.dumps(data, separators=(",", ":"))))

    def deserialize(self, data: bytes) -> dict[str,str]:
        data_hash = FileManager.stringify_sha1_hash(FileManager.get_hash_bytes(data))
        cached_item = self.get_cache().get(data_hash)
        if cached_item is not None:
            return cached_item
        else:
            temp_file_path = FileManager.get_temp_file_path()
            with open(temp_file_path, "wb") as f:
                f.write(data)
            process = subprocess.Popen([FileManager.LIB_EXIFTOOL_EXE_FILE, temp_file_path], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if stderr is not None:
                print(stderr)
                raise subprocess.CalledProcessError(process.returncode, process.args, stdout, stderr)
            if process.stdout is None:
                raise Exceptions.AttributeNoneError("stdout", process)
            output = {(key_value := line.split(": ", 1))[0].rstrip(): key_value[1] for line in stdout.decode().splitlines()}
            temp_file_path.unlink()
            output["sha1_hash"] = data_hash
            output.pop("ExifTool Version Number", None)
            output.pop("File Name", None)
            output.pop("Directory", None)
            output.pop("File Modification Date/Time", None)
            output.pop("File Access Date/Time", None)
            output.pop("File Creation Date/Time", None)
            output.pop("File Permissions", None)
            output.pop("Document Ancestors", None) # giant list of meaningless hashes
            output.pop("History Parameters", None)
            if "Error" in output:
                if output["Error"] == "Unknown file type":
                    output = {"sha1_hash": output["sha1_hash"]}
                else:
                    raise Exceptions.MediaSerializerFailedError(self, output["Error"])
            self.write_cache(data_hash, output)
            return output
