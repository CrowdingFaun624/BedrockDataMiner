from typing import Iterable, MutableMapping, TypeVar

import Structure.DataPath as DataPath
import Structure.DictStructure as DictStructure
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureSet as StructureSet
import Structure.StructureUtilities as SU
import Structure.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

d = TypeVar("d")

class KeymapStructure(DictStructure.DictStructure[d]):

    def __init__(
            self,
            name:str,
            field:str,
            keys:dict[tuple[str,type],Structure.Structure[d]|None],
            measure_length:bool,
            print_all:bool,
            tags:dict[str,list[str]],
            normalizer:list[Normalizer.Normalizer]|None,
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
        super().__init__(name, field, None, None, False, None, measure_length, print_all, normalizer, [], children_has_normalizer, children_tags)

        self.keys = keys
        self.tags = tags
        self.key_types:dict[str,set[type]] = {}

    def finalize(self) -> None:
        # During __init__, not all finals have been created yet, so self.types is not filled out yet. In finalize, it is filled out.
        self.check_initialization_parameters()
        for allowed_key, key_type in self.keys:
            if allowed_key not in self.key_types:
                self.key_types[allowed_key] = {key_type}
            else:
                self.key_types[allowed_key].add(key_type)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("keys", "a dict", True, TypeVerifier.DictTypeVerifier(dict, TypeVerifier.TupleTypeVerifier(tuple, "a tuple",
            TypeVerifier.TupleItemTypeVerifier(str, "a str"),
            TypeVerifier.TupleItemTypeVerifier(type, "a type"),
        ), (Structure.Structure, type(None)), "a dict", "a tuple", "a Structure or None")),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"), "a dict", "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a list or None", True, TypeVerifier.UnionTypeVerifier("a list or None", TypeVerifier.UnionTypeVerifier("a list or None", type(None), TypeVerifier.ListTypeVerifier(Normalizer.Normalizer, list, "a Normalizer", "a list", additional_function=lambda data: (sum(1 for item in data) > 0, "empty"))))),
        TypeVerifier.TypedDictKeyTypeVerifier("children_has_normalizer", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("children_tags", "a set", True, TypeVerifier.IterableTypeVerifier(str, set, "a str", "a set")),
    )

    def check_initialization_parameters(self) -> None:
        self.type_verifier.base_verify({
            "name": self.name,
            "field": self.field,
            "keys": self.keys,
            "measure_length": self.measure_length,
            "print_all": self.print_all,
            "tags": self.tags,
            "normalizer": self.normalizer,
            "children_has_normalizer": self.children_has_normalizer,
            "children_tags": self.children_tags,
        })

    def iter_structures(self) -> Iterable[Structure.Structure]:
        return (substructure for substructure in self.keys.values() if substructure is not None)

    def check_type(self, key:str, value:d) -> Trace.ErrorTrace|None:
        if isinstance(key, D.Diff) or isinstance(value, D.Diff):
            raise TypeError("`check_all_types` was given data containing Diffs!")
        if key not in self.key_types:
            return Trace.ErrorTrace(TypeError("Key, value %s: %s in %s excepted because key is not recognized!" % (SU.stringify(key), SU.stringify(value), self.name)), self.name, key, value)
        if type(value) not in self.key_types[key]:
            value_types_string = ", ".join(type_key.__name__ for type_key in self.key_types[key])
            return Trace.ErrorTrace(TypeError("Key, value %s: %s in %s excepted because value is %s instead of [%s]!" % (SU.stringify(key), SU.stringify(value), self.name, value.__class__.__name__, value_types_string)), self.name, key, value)

    def choose_structure_flat(self, key: str, value_type:type[d], value:d|None) -> tuple[Structure.Structure|None, list[Trace.ErrorTrace]]:
        output = self.keys.get((key, value_type), Structure.StructureFailure.choose_structure_failure)
        if output is Structure.StructureFailure.choose_structure_failure:
            accepted_types = [keys_key[1] for keys_key in self.keys.keys() if keys_key[0] == key]
            if len(accepted_types) == 0:
                return None, [Trace.ErrorTrace(KeyError("Unrecognized key %s for key, value %s: %s" % (self.name, key, value_type)), self.name, key, value)]
            else:
                return None, [Trace.ErrorTrace(KeyError("Unrecognized key type %s for key %s in %s (can only be [%s])" % (value_type, key, self.name, ", ".join(accepted_type.__name__ for accepted_type in accepted_types))), self.name, key, value)]
        return output, []

    def get_tag_paths(self, data: MutableMapping[str, d], tag: str, data_path: DataPath.DataPath) -> tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        output:list[DataPath.DataPath] = []
        exceptions:list[Trace.ErrorTrace] = []
        for key, value in data.items():
            if tag in self.tags[key]:
                output.append(data_path.copy((key, type(value))).embed(value))
            structure, new_exceptions = self.choose_structure_flat(key, type(value), value)
            for exception in new_exceptions: exception.add(self.name, key)
            exceptions.extend(new_exceptions)
            if structure is not None:
                new_tags, new_exceptions = structure.get_tag_paths(value, tag, data_path.copy((key, type(value))))
                output.extend(new_tags)
                for exception in new_exceptions: exception.add(self.name, key)
                exceptions.extend(new_exceptions)
        return output, exceptions

    def choose_structure(self, key:str, value:d) -> tuple[StructureSet.StructureSet, list[Trace.ErrorTrace]]:
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
