from typing import Iterable, MutableMapping, TypeVar

import Structure.DataPath as DataPath
import Structure.DictStructure as DictStructure
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureSet as StructureSet
import Structure.StructureUtilities as SU
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

d = TypeVar("d")

class KeymapStructure(DictStructure.DictStructure[d]):

    def __init__(
            self,
            name:str,
            field:str,
            measure_length:bool,
            print_all:bool,
            children_has_normalizer:bool,
            children_tags:set[str],
        ) -> None:
        super().__init__(name, field, False, None, measure_length, print_all, children_has_normalizer, children_tags)

        self.keys:dict[tuple[str,type],Structure.Structure[d]|None]|None = None
        self.tags:dict[str,list[str]]|None = None
        self.keys_intermediate:dict[str,dict[type,Structure.Structure|None]]|None = None
        self.key_types:dict[str,set[type]]|None = None

    def link_substructures(
            self,
            keys_intermediate:dict[str,dict[type,Structure.Structure|None]],
            normalizer:list[Normalizer.Normalizer],
            tags:dict[str,list[str]],
            ) -> None:
        self.keys_intermediate = keys_intermediate
        self.normalizer = normalizer
        self.tags = tags

    def finalize(self) -> None:
        if self.keys_intermediate is None:
            raise Exceptions.AttributeNoneError("keys_intermediate", self)
        self.keys = {}
        for key, substructure in self.keys_intermediate.items():
            for value_type, type_substructure in substructure.items():
                self.keys[key, value_type] = type_substructure
        self.key_types = {}
        for allowed_key, key_type in self.keys:
            if allowed_key not in self.key_types:
                self.key_types[allowed_key] = {key_type}
            else:
                self.key_types[allowed_key].add(key_type)

    def iter_structures(self) -> Iterable[Structure.Structure]:
        if self.keys is None:
            raise Exceptions.AttributeNoneError("keys", self)
        return (substructure for substructure in self.keys.values() if substructure is not None)

    def check_type(self, key:str, value:d) -> Trace.ErrorTrace|None:
        if self.key_types is None:
            raise Exceptions.AttributeNoneError("key_types", self)
        if key not in self.key_types:
            return Trace.ErrorTrace(Exceptions.StructureUnrecognizedKeyError(key), self.name, key, value)
        if type(value) not in self.key_types[key]:
            return Trace.ErrorTrace(Exceptions.StructureTypeError(tuple(self.key_types[key]), type(value), "Value"), self.name, key, value)

    def choose_structure_flat(self, key: str, value_type:type[d], value:d|None) -> tuple[Structure.Structure|None, list[Trace.ErrorTrace]]:
        if self.keys is None:
            raise Exceptions.AttributeNoneError("keys", self)
        output = self.keys.get((key, value_type), Structure.StructureFailure.choose_structure_failure)
        if output is Structure.StructureFailure.choose_structure_failure:
            accepted_types = [keys_key[1] for keys_key in self.keys.keys() if keys_key[0] == key]
            if len(accepted_types) == 0:
                return None, [Trace.ErrorTrace(Exceptions.StructureUnrecognizedKeyError(key), self.name, key, value)]
            else:
                return None, [Trace.ErrorTrace(Exceptions.StructureTypeError(tuple(accepted_types), value_type, "Value"), self.name, key, value)]
        return output, []

    def get_tag_paths(self, data: MutableMapping[str, d], tag: str, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        output:list[DataPath.DataPath] = []
        exceptions:list[Trace.ErrorTrace] = []
        if self.tags is None:
            raise Exceptions.AttributeNoneError("tags", self)
        for key, value in data.items():
            if tag in self.tags[key]:
                output.append(data_path.copy((key, type(value))).embed(value))
            structure, new_exceptions = self.choose_structure_flat(key, type(value), value)
            for exception in new_exceptions: exception.add(self.name, key)
            exceptions.extend(new_exceptions)
            if structure is not None:
                new_tags, new_exceptions = structure.get_tag_paths(value, tag, data_path.copy((key, type(value))), environment)
                output.extend(new_tags)
                for exception in new_exceptions: exception.add(self.name, key)
                exceptions.extend(new_exceptions)
        return output, exceptions

    def choose_structure(self, key:str, value:d) -> tuple[StructureSet.StructureSet, list[Trace.ErrorTrace]]:
        if self.keys is None:
            raise Exceptions.AttributeNoneError("keys", self)
        output:dict[D.DiffType,Structure.Structure|None] = {}
        exceptions:list[Trace.ErrorTrace] = []
        if self.detect_key_moves:
            iterator = D.double_iter_diff(key, value)
        else:
            key_iter = key.first_existing_property() if isinstance(key, D.Diff) else key
            iterator = ((key_iter, iter_diff_item[0], None, iter_diff_item[1]) for iter_diff_item in D.iter_diff(value))
        for key_iter, value_iter, key_diff_type, value_diff_type in iterator:
            structure = self.keys.get((key_iter, type(value_iter)), Structure.StructureFailure.choose_structure_failure)
            if structure is Structure.StructureFailure.choose_structure_failure:
                accepted_types = [keys_key[1] for keys_key in self.keys.keys() if keys_key[0] == key]
                if len(accepted_types) == 0:
                    exceptions.append(Trace.ErrorTrace(Exceptions.StructureUnrecognizedKeyError(key), self.name, key, value))
                else:
                    exceptions.append(Trace.ErrorTrace(Exceptions.StructureTypeError(tuple(accepted_types), type(value), "Value"), self.name, key, value))
                continue
            output[value_diff_type] = structure
        return StructureSet.StructureSet(output), exceptions
