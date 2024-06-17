import Structure.PassthroughStructure as PassthroughStructure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.Nbt.Endianness as Endianness
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.Nbt.NbtTypes as NbtTypes


class NbtBaseStructure(PassthroughStructure.PassthroughStructure[NbtTypes.TAG]):

    def __init__(
            self,
            name:str,
            endianness:Endianness.End,
            children_has_normalizer:bool,
            children_tags:set[str]
        ) -> None:
        super().__init__(name, name, children_has_normalizer, children_tags)

        self.endianness=endianness

    def normalize(self, data: NbtReader.NbtBytes, environment:StructureEnvironment.StructureEnvironment) -> tuple[NbtTypes.TAG|None, list[Trace.ErrorTrace]]:
        try:
            data_parsed = NbtReader.unpack_bytes(data.open(), gzipped=False, endianness=self.endianness)[1]
        except Exception as e:
            return None, [Trace.ErrorTrace(e, self.name, None, data)]
        new_output, exceptions = super().normalize(data_parsed, environment)
        if new_output is not None and new_output is not data_parsed:
            data_parsed = new_output
        return data_parsed, exceptions
