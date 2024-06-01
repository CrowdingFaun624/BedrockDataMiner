from typing import Any

import Downloader.Accessor as Accessor
import Downloader.Manager as Manager
import Version.Version as Version


class MyAccessor(Accessor.Accessor):

    def __init__(self, name: str, manager: Manager.Manager, version: "Version.Version", file_type_arguments:Any) -> None:
        super().__init__(name, manager, version, file_type_arguments)
        if "ipa" in self.version.tags:
            self.file_prepension = "Payload/minecraftpe.app/data/"
        elif "double_assets" in self.version.tags:
            self.file_prepension = "assets/assets/"
        else:
            self.file_prepension = "assets/"

    def modify_file_name(self, file_name: str = "") -> str:
        return self.file_prepension + file_name

    def trim_file_name(self, file_name: str) -> str:
        return file_name.replace(self.file_prepension, "", 1)
