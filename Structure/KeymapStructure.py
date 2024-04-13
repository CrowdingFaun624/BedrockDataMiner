from typing import TypeVar

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

        self.name = name
        self.keys = keys
        self.detect_key_moves = False
        self.measure_length = measure_length
        self.print_all = print_all
        self.tags = tags
        self.normalizer = normalizer
        self.children_has_normalizer = children_has_normalizer
        self.children_tags = children_tags
        self.check_initialization_parameters()
        self.key_types:dict[str,set[type]] = {}

    def finalize(self) -> None:
        # During __init__, not all finals have been created yet, so self.types is not filled out yet. In finalize, it is filled out.
        for allowed_key, key_type in self.keys:
            if allowed_key not in self.key_types:
                self.key_types[allowed_key] = {key_type}
            else:
                self.key_types[allowed_key].add(key_type)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
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
            "keys": self.keys,
            "measure_length": self.measure_length,
            "print_all": self.print_all,
            "tags": self.tags,
            "normalizer": self.normalizer,
            "children_has_normalizer": self.children_has_normalizer,
            "children_tags": self.children_tags,
        })

    def check_type(self, key:str, value:d, trace:Trace.Trace) -> tuple[Trace.Trace,Exception]|None:
        if isinstance(key, D.Diff) or isinstance(value, D.Diff):
            raise TypeError("`check_all_types` was given data containing Diffs!")
        if key not in self.key_types:
            return (trace.copy(self.name, key), TypeError("Key, value %s: %s in %s excepted because key is not recognized!" % (SU.stringify(key), SU.stringify(value), self.name)))
        if type(value) not in self.key_types[key]:
            value_types_string = ", ".join(type_key.__name__ for type_key in self.key_types[key])
            return (trace.copy(self.name, key), TypeError("Key, value %s: %s in %s excepted because value is %s instead of [%s]!" % (SU.stringify(key), SU.stringify(value), self.name, value.__class__.__name__, value_types_string)))

    def choose_structure_flat(self, key: str, value:type[d], trace: Trace.Trace) -> Structure.Structure | None:
        exception = None
        try:
            return self.keys[key, value]
        except Exception as e:
            exception = e
            exception.args = tuple(list(exception.args) + ["Failed to get Structure in %s in %s for key, value %s: %s" % (self.name, trace, key, value)])
        if exception is not None:
            raise exception

    def choose_structure(self, key:str, value:d, trace:Trace.Trace) -> StructureSet.StructureSet:
        output:dict[D.DiffType,Structure.Structure|None] = {}
        if self.detect_key_moves:
            iterator = D.double_iter_diff(key, value)
        else:
            key_iter = key.first_existing_property() if isinstance(key, D.Diff) else key
            iterator = ((key_iter, iter_diff_item[0], None, iter_diff_item[1]) for iter_diff_item in D.iter_diff(value))
        for key_iter, value_iter, key_diff_type, value_diff_type in iterator:
            exception:Exception|None = None
            try:
                output[value_diff_type] = self.keys[key_iter, type(value_iter)]
            except Exception as e:
                exception = e
                exception.args = tuple(list(exception.args) + ["Failed to get Structure in %s in %s for key, value %s: %s" % (self.name, trace, key_iter, value_iter)])
            if exception is not None:
                raise exception
        return StructureSet.StructureSet(output)
