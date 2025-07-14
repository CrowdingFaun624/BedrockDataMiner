from types import EllipsisType

from Structure.AbstractPassthroughStructure import AbstractPassthroughStructure
from Structure.Container import Con
from Structure.SimpleContainer import SCon
from Structure.StructureEnvironment import PrinterEnvironment
from Utilities.Exceptions import StructureTypeError
from Utilities.Trace import Trace


class PassthroughStructure[D, BO, CO](AbstractPassthroughStructure[D, D, BO, CO]):

    __slots__ = ()

    def normalize(self, data: D, trace: Trace, environment: PrinterEnvironment) -> D|EllipsisType:
        with trace.enter(self, self.trace_name, data):
            if not isinstance(data, self.pre_normalized_types):
                trace.exception(StructureTypeError(self.pre_normalized_types, type(data), "Data", "(pre-normalized)"))
                return ...

            data, pre_data_identity_changed = self.normalizer_pass(self.normalizers, data, trace, environment)

            structure = self.get_structure(data, trace, environment)
            if structure is not None and structure.children_has_normalizer:
                normalizer_output = structure.normalize(data, trace, environment)
                if normalizer_output is not ...:
                    pre_data_identity_changed = True
                    data = normalizer_output

            data, post_data_identity_changed = self.normalizer_pass(self.post_normalizers, data, trace, environment)

            return data if pre_data_identity_changed or post_data_identity_changed else ...
        return ...

    def containerize(self, data: D, trace: Trace, environment: PrinterEnvironment) -> Con[D] | EllipsisType:
        with trace.enter(self, self.trace_name, data):
            structure = self.get_structure(data, trace, environment)
            if structure is None:
                return SCon(data, environment.domain)
            else:
                return structure.containerize(data, trace, environment)
        return ...
