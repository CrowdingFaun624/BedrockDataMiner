from types import EllipsisType
from typing import Sequence

from Serializer.Serializer import Serializer
from Structure.AbstractPassthroughStructure import AbstractPassthroughStructure
from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.Normalizer import Normalizer
from Structure.SimpleContainer import SCon
from Structure.Structure import Structure
from Structure.StructureEnvironment import PrinterEnvironment
from Utilities.Exceptions import StructureTypeError
from Utilities.File import AbstractFile
from Utilities.Trace import Trace


class FileStructure[D, BO, CO](AbstractPassthroughStructure[AbstractFile[D], D, BO, CO]):

    __slots__ = (
        "content_types",
        "file_types",
        "serializer",
        "structure",
    )

    def link_file_structure(
        self,
        content_types:tuple[type,...],
        file_types:tuple[type,...],
        serializer:Serializer|None,
        structure:Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None,
    ) -> None:
        self.content_types = content_types
        self.file_types = file_types
        self.serializer = serializer
        self.structure = structure

    def get_structure(self, data: D, trace: Trace, environment: PrinterEnvironment) -> Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None:
        return self.structure

    def iter_structures(self) -> Sequence[Structure]:
        return (self.structure,) if self.structure is not None else ()

    def normalize(self, data: AbstractFile[D], trace: Trace, environment: PrinterEnvironment) -> AbstractFile[D]|EllipsisType:
        with trace.enter(self, self.name, data):
            if not isinstance(data, self.pre_normalized_types):
                trace.exception(StructureTypeError(self.pre_normalized_types, type(data), "Data", "(pre-normalized)"))
                return ...

            data, pre_data_identity_changed = self.normalizer_pass(self.normalizers, data, environment)
            if not isinstance(data, self.file_types):
                trace.exception(StructureTypeError(self.file_types, type(data), "Data", "(after normalizer pass)"))

            structure = self.get_structure(data.read(self.serializer), trace, environment)
            if structure is not None and structure.children_has_normalizer:
                normalizer_output = structure.normalize(data.read(self.serializer), trace, environment)
                if normalizer_output is not ...:
                    pre_data_identity_changed = True
                    data.set_data(self.serializer, normalizer_output)

            data, post_data_identity_changed = self.normalizer_pass(self.post_normalizers, data, environment)
            if not isinstance(data, self.file_types):
                trace.exception(StructureTypeError(self.file_types, type(data), "Data", "(after post-normalizer pass)"))

            return data if pre_data_identity_changed or post_data_identity_changed else ...
        return ...

    def normalizer_pass(self, normalizers: Sequence[Normalizer], data: AbstractFile[D], environment: PrinterEnvironment) -> tuple[AbstractFile[D], bool]:
        data_identity_changed:bool = False
        for normalizer in normalizers:
            if not normalizer.filter_pass(environment.structure_info):
                continue
            if isinstance(data, AbstractFile):
                normalizer_output = normalizer(data.read(self.serializer))
                if normalizer_output is not None:
                    # no need to set `data_identity_changed`
                    data.set_data(self.serializer, normalizer_output)
            else:
                normalizer_output = normalizer(data)
                if normalizer_output is not None:
                    data_identity_changed = True
                    data = normalizer_output
        return data, data_identity_changed

    def containerize(self, data: AbstractFile[D], trace: Trace, environment: PrinterEnvironment) -> Con[D] | EllipsisType:
        with trace.enter(self, self.name, data):
            structure = self.get_structure(data.read(self.serializer), trace, environment)
            if structure is None:
                return SCon(data.read(self.serializer), environment.domain)
            else:
                return structure.containerize(data.read(self.serializer), trace, environment)
        return ...

    def type_check_extra(self, data: Con[D], trace: Trace, environment: PrinterEnvironment) -> None:
        if not isinstance(data.data, self.content_types):
            trace.exception(StructureTypeError(self.content_types, type(data.data), "Data"))
