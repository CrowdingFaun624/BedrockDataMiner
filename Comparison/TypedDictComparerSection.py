from typing import Any, TypeVar

import Comparison.ComparerSection as ComparerSection
import Comparison.ComparerSet as ComparerSet
import Comparison.ComparisonUtilities as CU
import Comparison.DictComparerSection as DictComparerSection
import Comparison.Difference as D
import Comparison.Normalizer as Normalizer
import Comparison.Trace as Trace
import Comparison.Modifier as Modifier
import Utilities.TypeVerifier as TypeVerifier

d = TypeVar("d")

class TypedDictComparerSection(DictComparerSection.DictComparerSection[d]):

    def __init__(
            self,
            name:str,
            types:dict[tuple[str,type],ComparerSection.ComparerSection[d]|None],
            measure_length:bool=False,
            print_all:bool=False,
            normalizer:list[Normalizer.Normalizer]|None=None,
            children_has_normalizer:bool=False,
            modifier:Modifier.Modifier|None=None
        ) -> None:
        ''' * `name` is what the key of this dictionary is.
         * `types` is a dictionary with keys of tuples of strings and types and values of comparer sections or Nones.
         * `types` is indexed using the key and the type of the key.
         * If a value of `types` is a ComparerSection, then it will compare and print values using that ComparerSection.
         * If a value of `types` is None, then it will use `stringify` in place of a printer and not compare.
         * If `measure_length` is True, then it will show how the length of the data changed when comparing.
         * If `print_all` is True, then if there is a change in one part of the data, then all parts will be printed.
         * `normalizer` is a list of normalizer functions that modify the data without returning anything.'''

        self.name = name
        self.types = types
        self.detect_key_moves = False
        self.measure_length = measure_length
        self.print_all = print_all
        self.normalizer = normalizer
        self.children_has_normalizer = children_has_normalizer
        self.modifier = modifier
        if self.modifier is not None:
            self.modifier.give_comparer_section(self)
        self.check_initialization_parameters()
        self.key_types:dict[str,set[type]] = {}

    def modifier_modify(self, data:Any) -> None:
        return super().modifier_modify(data)

    def finalize(self) -> None:
        # During __init__, not all finals have been created yet, so self.types is not filled out yet. In finalize, it is filled out.
        for allowed_key, key_type in self.types:
            if allowed_key not in self.key_types:
                self.key_types[allowed_key] = {key_type}
            else:
                self.key_types[allowed_key].add(key_type)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a dict", True, TypeVerifier.DictTypeVerifier(dict, TypeVerifier.TupleTypeVerifier(tuple, "a tuple",
            TypeVerifier.TupleItemTypeVerifier(str, "a str"),
            TypeVerifier.TupleItemTypeVerifier(type, "a type"),
        ), (ComparerSection.ComparerSection, type(None)), "a dict", "a tuple", "a ComparerSection or None")),
        TypeVerifier.TypedDictKeyTypeVerifier("measure_length", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("print_all", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a list or None", True, TypeVerifier.UnionTypeVerifier("a list or None", TypeVerifier.UnionTypeVerifier("a list or None", type(None), TypeVerifier.ListTypeVerifier(Normalizer.Normalizer, list, "a Normalizer", "a list", additional_function=lambda data: (sum(1 for item in data) > 0, "empty"))))),
        TypeVerifier.TypedDictKeyTypeVerifier("children_has_normalizer", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("modifier", "a Modifier or None", True, (Modifier.Modifier, type(None))),
    )

    def check_initialization_parameters(self) -> None:
        self.type_verifier.base_verify({
            "name": self.name,
            "types": self.types,
            "measure_length": self.measure_length,
            "print_all": self.print_all,
            "normalizer": self.normalizer,
            "children_has_normalizer": self.children_has_normalizer,
            "modifier": self.modifier,
        })

    def check_type(self, key:str, value:d, trace:Trace.Trace) -> tuple[Trace.Trace,Exception]|None:
        if isinstance(key, D.Diff) or isinstance(value, D.Diff):
            raise TypeError("`check_all_types` was given data containing Diffs!")
        if key not in self.key_types:
            return (trace.copy(self.name, key), TypeError("Key, value %s: %s in %s excepted because key is not recognized!" % (CU.stringify(key), CU.stringify(value), self.name)))
        if type(value) not in self.key_types[key]:
            value_types_string = ", ".join(type_key.__name__ for type_key in self.key_types[key])
            return (trace.copy(self.name, key), TypeError("Key, value %s: %s in %s excepted because value is %s instead of [%s]!" % (CU.stringify(key), CU.stringify(value), self.name, value.__class__.__name__, value_types_string)))

    def choose_comparer_flat(self, key: str, value:type[d], trace: Trace.Trace) -> ComparerSection.ComparerSection | None:
        exception = None
        try:
            return self.types[key, value]
        except Exception as e:
            exception = e
            exception.args = tuple(list(exception.args) + ["Failed to get comparer in %s in %s for key, value %s: %s" % (self.name, trace, key, value)])
        if exception is not None:
            raise exception

    def choose_comparer(self, key:str, value:d, trace:Trace.Trace) -> ComparerSet.ComparerSet:
        output:dict[D.DiffType,ComparerSection.ComparerSection|None] = {}
        if self.detect_key_moves:
            iterator = D.double_iter_diff(key, value)
        else:
            key_iter = key.first_existing_property() if isinstance(key, D.Diff) else key
            iterator = ((key_iter, iter_diff_item[0], None, iter_diff_item[1]) for iter_diff_item in D.iter_diff(value))
        for key_iter, value_iter, key_diff_type, value_diff_type in iterator:
            exception:Exception|None = None
            try:
                output[value_diff_type] = self.types[key_iter, type(value_iter)]
            except Exception as e:
                exception = e
                exception.args = tuple(list(exception.args) + ["Failed to get comparer in %s in %s for key, value %s: %s" % (self.name, trace, key_iter, value_iter)])
            if exception is not None:
                raise exception
        return ComparerSet.ComparerSet(output)
