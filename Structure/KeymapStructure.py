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
        ''' * `name` is what the key of this dictionary is.
         * `types` is a dictionary with keys of tuples of strings and types and values of Structures or Nones.
         * `types` is indexed using the key and the type of the key.
         * If a value of `types` is a Structure, then it will compare and print values using that Structure.
         * If a value of `types` is None, then it will use `stringify` in place of a printer and not compare.
         * If `measure_length` is True, then it will show how the length of the data changed when comparing.
         * If `print_all` is True, then if there is a change in one part of the data, then all parts will be printed.
         * `normalizer` is a list of normalizer functions that modify the data without returning anything.'''
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
        assert self.keys_intermediate is not None
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
        assert self.keys is not None
        return (substructure for substructure in self.keys.values() if substructure is not None)

    def check_type(self, key:str, value:d) -> Trace.ErrorTrace|None:
        if isinstance(key, D.Diff) or isinstance(value, D.Diff):
            raise TypeError("`check_all_types` was given data containing Diffs!")
        assert self.key_types is not None
        if key not in self.key_types:
            return Trace.ErrorTrace(TypeError("Key, value %s: %s in %s excepted because key is not recognized!" % (SU.stringify(key), SU.stringify(value), self.name)), self.name, key, value)
        if type(value) not in self.key_types[key]:
            value_types_string = ", ".join(type_key.__name__ for type_key in self.key_types[key])
            return Trace.ErrorTrace(TypeError("Key, value %s: %s in %s excepted because value is %s instead of [%s]!" % (SU.stringify(key), SU.stringify(value), self.name, value.__class__.__name__, value_types_string)), self.name, key, value)

    def choose_structure_flat(self, key: str, value_type:type[d], value:d|None) -> tuple[Structure.Structure|None, list[Trace.ErrorTrace]]:
        assert self.keys is not None
        output = self.keys.get((key, value_type), Structure.StructureFailure.choose_structure_failure)
        if output is Structure.StructureFailure.choose_structure_failure:
            accepted_types = [keys_key[1] for keys_key in self.keys.keys() if keys_key[0] == key]
            if len(accepted_types) == 0:
                return None, [Trace.ErrorTrace(KeyError("Unrecognized key %s for key, value %s: %s" % (self.name, key, value_type)), self.name, key, value)]
            else:
                return None, [Trace.ErrorTrace(KeyError("Unrecognized key type %s for key %s in %s (can only be [%s])" % (value_type, key, self.name, ", ".join(accepted_type.__name__ for accepted_type in accepted_types))), self.name, key, value)]
        return output, []

    def get_tag_paths(self, data: MutableMapping[str, d], tag: str, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        output:list[DataPath.DataPath] = []
        exceptions:list[Trace.ErrorTrace] = []
        assert self.tags is not None
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
        assert self.keys is not None
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
                    exceptions.append(Trace.ErrorTrace(KeyError("Unrecognized key %s for key, value %s: %s" % (self.name, key, type(value))), self.name, key, value))
                else:
                    exceptions.append(Trace.ErrorTrace(KeyError("Unrecognized key type %s for key %s in %s (can only be [%s])" % (type(value), key, self.name, ", ".join(accepted_type.__name__ for accepted_type in accepted_types))), self.name, key, value))
                continue
            output[value_diff_type] = structure
        return StructureSet.StructureSet(output), exceptions
