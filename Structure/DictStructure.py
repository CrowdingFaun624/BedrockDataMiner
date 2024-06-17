from typing import Any, Callable, Iterable, MutableMapping, TypeVar

import Structure.AbstractMappingStructure as AbstractMappingStructure
import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureSet as StructureSet
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions
import Utilities.Nbt.NbtTypes as NbtTypes

d = TypeVar("d")

class DictStructure(AbstractMappingStructure.AbstractMappingStructure[d]):

    valid_types = (dict, NbtTypes.TAG_Compound)

    def __init__(
            self,
            name:str,
            field:str,
            detect_key_moves:bool,
            comparison_move_function:Callable[[str, d], Any]|None,
            measure_length:bool,
            print_all:bool,
            children_has_normalizer:bool,
            children_tags:set[str],
        ) -> None:
        super().__init__(name, field, detect_key_moves, comparison_move_function, measure_length, print_all, children_has_normalizer, children_tags)

        self.structure:Structure.Structure[d]|None = None
        self.types:tuple[type,...]|None = None

    def link_substructures(
        self,
        structure:Structure.Structure[d]|None,
        types:list[type],
        normalizer:list[Normalizer.Normalizer],
        tags:list[str],
    ) -> None:
        super().link_substructures(normalizer, tags)
        self.structure = structure
        self.types = tuple(types)

    def iter_structures(self) -> Iterable[Structure.Structure]:
        if self.structure is None: return []
        else: return [self.structure]

    def check_type(self, key:str, value:d) -> Trace.ErrorTrace|None:
        if self.types is None:
            raise Exceptions.AttributeNoneError("types", self)
        if not isinstance(value, self.types):
            return Trace.ErrorTrace(Exceptions.StructureTypeError(self.types, type(value), "Value"), self.name, key, value)

    def get_tag_paths(self, data: MutableMapping[str, d], tag: str, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        output:list[DataPath.DataPath] = []
        exceptions:list[Trace.ErrorTrace] = []
        if self.tags is None:
            raise Exceptions.AttributeNoneError("tags", self)
        if tag in self.tags:
            output.extend(data_path.copy((key, type(value))).embed(value) for key, value in data.items())
        for key, value in data.items():
            structure, new_exceptions = self.choose_structure_flat(key, type(value), value)
            for exception in new_exceptions: exception.add(self.name, key)
            exceptions.extend(new_exceptions)
            if structure is not None:
                new_tags, new_exceptions = structure.get_tag_paths(value, tag, data_path.copy((key, type(value))), environment)
                output.extend(new_tags)
                for exception in new_exceptions: exception.add(self.name, key)
                exceptions.extend(new_exceptions)
        return output, exceptions

    def choose_structure_flat(self, key:str, value_type: type[d], value:d|None) -> tuple[Structure.Structure|None, list[Trace.ErrorTrace]]:
        return self.structure, []

    def choose_structure(self, key:str|D.Diff[str,str], value:d|D.Diff[d,d]) -> tuple[StructureSet.StructureSet, list[Trace.ErrorTrace]]:
        return StructureSet.StructureSet({value_diff_type: self.structure for value_iter, value_diff_type in D.iter_diff(value)}), []
