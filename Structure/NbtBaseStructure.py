from typing import Iterable

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureSet as StructureSet
import Structure.StructureUtilities as SU
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions
import Utilities.Nbt.Endianness as Endianness
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.Nbt.NbtTypes as NbtTypes


class NbtBaseStructure(Structure.Structure[NbtTypes.TAG]):

    def __init__(
            self,
            name:str,
            endianness:Endianness.End,
            children_has_normalizer:bool,
            children_tags:set[str]
        ) -> None:
        super().__init__(name, name, children_has_normalizer, children_tags)

        self.endianness=endianness

        self.structure:Structure.Structure|None = None
        self.types:tuple[type,...]|None = None
        self.normalizer:list[Normalizer.Normalizer]|None = None

    def link_substructures(
        self,
        structure:Structure.Structure,
        types:list[type],
        normalizer:list[Normalizer.Normalizer],
    ) -> None:
        self.structure = structure
        self.types = tuple(types)
        self.normalizer = normalizer

    def iter_structures(self) -> Iterable[Structure.Structure]:
        if self.structure is None:
            raise Exceptions.AttributeNoneError("structure", self)
        else: return [self.structure]

    def check_all_types(self, data: NbtTypes.TAG, environment:StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        output:list[Trace.ErrorTrace] = []
        if self.types is None:
            raise Exceptions.AttributeNoneError("types", self)
        if not isinstance(data, self.types):
            output.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.types, type(data), "Data"), self.name, None, data))
            return output
        structure, new_exceptions = self.choose_structure_flat(None, type(data), data)
        for exception in new_exceptions: exception.add(self.name, None)
        output.extend(new_exceptions)
        if structure is not None:
            new_exceptions = structure.check_all_types(data, environment)
            for exception in new_exceptions: exception.add(self.name, None)
            output.extend(new_exceptions)
        return output

    def choose_structure_flat(self, key:None, value_type:type[NbtTypes.TAG], value:NbtTypes.TAG|None) -> tuple[Structure.Structure|None, list[Trace.ErrorTrace]]:
        return self.structure, []

    def choose_structure(self, item:NbtTypes.TAG|D.Diff[NbtTypes.TAG,NbtTypes.TAG]) -> tuple[StructureSet.StructureSet,list[Trace.ErrorTrace]]:
        return StructureSet.StructureSet({diff_type: self.structure for item_iter, diff_type in D.iter_diff(item)}), []

    def normalize(self, data: NbtReader.NbtBytes, environment:StructureEnvironment.StructureEnvironment) -> tuple[NbtTypes.TAG|None, list[Trace.ErrorTrace]]:
        try:
            data_parsed = NbtReader.unpack_bytes(data.open(), gzipped=False, endianness=self.endianness)[1]
        except Exception as e:
            return None, [Trace.ErrorTrace(e, self.name, None, data)]
        if not self.children_has_normalizer: return data_parsed, []
        if self.normalizer is None:
            raise Exceptions.AttributeNoneError("normalizer", self)
        for normalizer in self.normalizer:
            try:
                normalizer(data_parsed)
            except Exception as e:
                return None, [Trace.ErrorTrace(e, self.name, None, data)]
        exceptions:list[Trace.ErrorTrace] = []
        structure, new_exceptions = self.choose_structure_flat(None, type(data_parsed), data_parsed)
        for exception in new_exceptions: exception.add(self.name, None)
        exceptions.extend(new_exceptions)
        if structure is not None:
            normalize_output, new_exceptions = structure.normalize(data_parsed, environment)
            for exception in new_exceptions: exception.add(self.name, None)
            exceptions.extend(new_exceptions)
            if normalize_output is not None:
                data_parsed = normalize_output
        return data_parsed, exceptions

    def get_tag_paths(self, data: NbtTypes.TAG, tag: str, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath], list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        exceptions:list[Trace.ErrorTrace] = []
        structure, new_exceptions = self.choose_structure_flat(None, type(data), data)
        for exception in new_exceptions: exception.add(self.name, None)
        exceptions.extend(new_exceptions)
        if structure is None: return [], exceptions
        output, new_exceptions = structure.get_tag_paths(data, tag, data_path.copy(("", type(data))), environment)
        for exception in new_exceptions: exception.add(self.name, None)
        exceptions.extend(new_exceptions)
        return output, exceptions

    def compare(self, data1: NbtTypes.TAG, data2: NbtTypes.TAG, environment:StructureEnvironment.StructureEnvironment) -> tuple[NbtTypes.TAG|D.Diff[NbtTypes.TAG, NbtTypes.TAG], bool, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        structure_set, new_exceptions = self.choose_structure(D.Diff(data1, data2))
        for exception in new_exceptions: exception.add(self.name, None)
        exceptions.extend(new_exceptions)
        output, has_changes, new_exceptions = structure_set.compare(data1, data2, environment)
        for exception in new_exceptions: exception.add(self.name, None)
        exceptions.extend(new_exceptions)
        return output, has_changes, exceptions

    def print_text(self, data: NbtTypes.TAG, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line], list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        structure, new_exceptions = self.choose_structure(data)
        for exception in new_exceptions: exception.add(self.name, None)
        exceptions.extend(new_exceptions)
        output, new_exceptions = structure.print_text(D.DiffType.not_diff, data, environment)
        for exception in new_exceptions: exception.add(self.name, None)
        exceptions.extend(new_exceptions)
        return output, exceptions

    def compare_text(self, data:NbtTypes.TAG|D.Diff[NbtTypes.TAG,NbtTypes.TAG], environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line], bool, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        structure_set, new_exceptions = self.choose_structure(data)
        for exception in new_exceptions: exception.add(self.name, None)
        exceptions.extend(new_exceptions)
        if isinstance(data, D.Diff):
            output:list[SU.Line] = []
            match data.change_type:
                case D.ChangeType.addition:
                    new_exceptions = self.print_single(None, data.new, "Added", output, structure_set[D.DiffType.new], environment)
                case D.ChangeType.change:
                    new_exceptions = self.print_double(None, data.old, data.new, "Changed", output, structure_set, environment)
                case D.ChangeType.removal:
                    new_exceptions = self.print_single(None, data.old, "Removed", output, structure_set[D.DiffType.old], environment)
            for exception in new_exceptions: exception.add(self.name, None)
            exceptions.extend(new_exceptions)
            return output, True, exceptions
        else:
            output, has_changes, new_exceptions = structure_set.compare_text(D.DiffType.not_diff, data, environment)
            for exception in new_exceptions: exception.add(self.name, None)
            exceptions.extend(new_exceptions)
            return output, has_changes, exceptions
