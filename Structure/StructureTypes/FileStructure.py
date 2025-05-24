from types import EllipsisType
from typing import Sequence

import Serializer.Serializer as Serializer
import Structure.AbstractPassthroughStructure as AbstractPassthroughStructure
import Structure.Container as Con
import Structure.Difference as Diff
import Structure.Normalizer as Normalizer
import Structure.SimpleContainer as SCon
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Exceptions as Exceptions
import Utilities.File as File
import Utilities.Trace as Trace


class FileStructure[D, BO, CO](AbstractPassthroughStructure.AbstractPassthroughStructure[File.AbstractFile[D], D, BO, CO]):

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
        serializer:Serializer.Serializer|None,
        structure:Structure.Structure[D, Con.Con[D], Con.Don[D], Con.Don[D]|Diff.Diff[Con.Don[D]], BO, CO]|None,
    ) -> None:
        self.content_types = content_types
        self.file_types = file_types
        self.serializer = serializer
        self.structure = structure

    def get_structure(self, data: D, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> Structure.Structure[D, Con.Con[D], Con.Don[D], Con.Don[D]|Diff.Diff[Con.Don[D]], BO, CO]|None:
        return self.structure

    def iter_structures(self) -> Sequence[Structure.Structure]:
        return (self.structure,) if self.structure is not None else ()

    def normalize(self, data: File.AbstractFile[D], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> File.AbstractFile[D]|EllipsisType:
        with trace.enter(self, self.name, data):
            if not isinstance(data, self.pre_normalized_types):
                trace.exception(Exceptions.StructureTypeError(self.pre_normalized_types, type(data), "Data", "(pre-normalized)"))
                return ...

            data, pre_data_identity_changed = self.normalizer_pass(self.normalizers, data, environment)
            if not isinstance(data, self.file_types):
                trace.exception(Exceptions.StructureTypeError(self.file_types, type(data), "Data", "(after normalizer pass)"))

            structure = self.get_structure(data.read(self.serializer), trace, environment)
            if structure is not None and structure.children_has_normalizer:
                normalizer_output = structure.normalize(data.read(self.serializer), trace, environment)
                if normalizer_output is not ...:
                    pre_data_identity_changed = True
                    data.set_data(self.serializer, normalizer_output)

            data, post_data_identity_changed = self.normalizer_pass(self.post_normalizers, data, environment)
            if not isinstance(data, self.file_types):
                trace.exception(Exceptions.StructureTypeError(self.file_types, type(data), "Data", "(after post-normalizer pass)"))

            return data if pre_data_identity_changed or post_data_identity_changed else ...
        return ...

    def normalizer_pass(self, normalizers: Sequence[Normalizer.Normalizer], data: File.AbstractFile[D], environment: StructureEnvironment.PrinterEnvironment) -> tuple[File.AbstractFile[D], bool]:
        data_identity_changed:bool = False
        for normalizer in normalizers:
            if not normalizer.filter_pass(environment.structure_info):
                continue
            if isinstance(data, File.AbstractFile):
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

    def containerize(self, data: File.AbstractFile[D], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> Con.Con[D] | EllipsisType:
        with trace.enter(self, self.name, data):
            structure = self.get_structure(data.read(self.serializer), trace, environment)
            if structure is None:
                return SCon.SCon(data.read(self.serializer), environment.domain)
            else:
                return structure.containerize(data.read(self.serializer), trace, environment)
        return ...

    def type_check_extra(self, data: Con.Con[D], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> None:
        if not isinstance(data.data, self.content_types):
            trace.exception(Exceptions.StructureTypeError(self.content_types, type(data.data), "Data"))
