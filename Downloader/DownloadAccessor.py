from datetime import datetime
from typing import TYPE_CHECKING, BinaryIO, TypedDict

from Component.ComponentFunctions import register_builtin
from Downloader.Accessor import Accessor
from Downloader.FileAccessor import FileAccessor
from Utilities.Log import Log
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

if TYPE_CHECKING:
    import requests

class InstanceArgumentsTypedDict(TypedDict):
    url: str

class ArgumentsTypedDict(TypedDict):
    location: str
    log: str

@register_builtin()
class DownloadAccessor(FileAccessor):
    
    instance_parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("url", True, str),
    )

    class_parameters = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("location", True, str),
        TypedDictKeyTypeVerifier("log", False, (str, type(None))),
    )

    __slots__ = (
        "_installed",
        "file_handle",
        "location",
        "log",
        "url",
    )

    def prepare_for_install(self, instance_arguments:InstanceArgumentsTypedDict, class_arguments:ArgumentsTypedDict, linked_accessors:dict[str,Accessor]) -> None:
        version_directory = self.version.version_directory
        location = version_directory.joinpath(class_arguments["location"])
        self.location = location
        self._installed:bool|None = None
        self.file_handle:BinaryIO|None = None
        self.log = self.domain.script_referenceable.get(class_arguments["log"], Log) if "log" in class_arguments else None

        self.url = instance_arguments["url"]

    @property
    def installed(self) -> bool:
        if self._installed is None:
            self._installed = self.location.exists()
        return self._installed

    def log_response(self, response:"requests.Response") -> "requests.Response":
        if self.log is not None and self.log.supports_type(self.log, dict):
            self.log.write({
                "version": self.version.name,
                "time": datetime.now().isoformat(),
                "status_code": response.status_code,
                "headers": {key: value for key, value in response.headers.items()},
                "url": response.url,
                "reason": response.reason,
                "elapsed": str(response.elapsed),
                "actual_response_length": len(response.content)
            })
        return response

    def open(self) -> BinaryIO:
        self.install()
        if self.file_handle is None:
            self.file_handle = open(self.location, "rb")
        return self.file_handle

    def close(self) -> None:
        super().close()
        if self.file_handle is not None:
            self.file_handle.close()
            self.file_handle = None

    def install(self) -> None:
        if not self.installed:
            import requests
            with open(self.location, "wb") as f, requests.get(self.url) as response:
                f.write(self.log_response(response).content)
            self._installed = True

    def all_done(self) -> None:
        super().all_done()
        self._installed = False
        if self.file_handle is not None:
            self.file_handle.close()
        if self.location.exists():
            self.location.unlink()
