import Downloader.Accessor as Accessor

__all__ = ["ZipAccessor"]

class ZipAccessor(Accessor.SubDirectoryAccessor):

    def initialize(self) -> None:
        if self.version.has_tag("ipa"):
            self.file_prepension = "Payload/minecraftpe.app/data/"
        elif self.version.has_tag("double_assets"):
            self.file_prepension = "assets/assets/"
        else:
            self.file_prepension = "assets/"
