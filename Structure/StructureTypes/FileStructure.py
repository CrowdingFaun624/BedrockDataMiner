from types import EllipsisType

from Serializer.Serializer import Serializer
from Structure.StructureEnvironment import PrinterEnvironment
from Structure.WithinStructure import WithinStructure
from Utilities.File import AbstractFile
from Utilities.Trace import Trace


class FileStructure[D, BO, CO](WithinStructure[AbstractFile[D], D, BO, CO]):

    __slots__ = (
        "serializer",
    )

    def finalize_file_structure(self, serializer:Serializer|None) -> None:
        self.serializer = serializer

    def get_insides(self, data: AbstractFile[D], trace: Trace, environment: PrinterEnvironment) -> D|EllipsisType:
        return data.read(self.serializer)
