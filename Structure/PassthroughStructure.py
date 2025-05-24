from types import EllipsisType

import Structure.AbstractPassthroughStructure as AbstractPassthroughStructure
import Structure.Container as Con
import Structure.SimpleContainer as SCon
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace


class PassthroughStructure[D, BO, CO](AbstractPassthroughStructure.AbstractPassthroughStructure[D, D, BO, CO]):

    __slots__ = ()

    def normalize(self, data: D, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> D|EllipsisType:
        with trace.enter(self, self.name, data):
            if not isinstance(data, self.pre_normalized_types):
                trace.exception(Exceptions.StructureTypeError(self.pre_normalized_types, type(data), "Data", "(pre-normalized)"))
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

    def containerize(self, data: D, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> Con.Con[D] | EllipsisType:
        with trace.enter(self, self.name, data):
            structure = self.get_structure(data, trace, environment)
            if structure is None:
                return SCon.SCon(data, environment.domain)
            else:
                return structure.containerize(data, trace, environment)
        return ...
