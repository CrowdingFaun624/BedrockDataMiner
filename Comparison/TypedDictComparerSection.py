from typing import TypeVar

import Comparison.ComparerSection as ComparerSection
import Comparison.ComparerSet as ComparerSet
import Comparison.ComparisonUtilities as CU
import Comparison.DictComparerSection as DictComparerSection
import Comparison.Difference as D
import Comparison.Normalizer as Normalizer
import Comparison.Trace as Trace

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
        self.check_initialization_parameters()

    def check_initialization_parameters(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("`name` is not a str!")
        if not isinstance(self.types, dict):
            raise TypeError("`types` is not a dict!")
        for index, (key, value) in enumerate(self.types.items()):
            if not isinstance(key, tuple):
                raise TypeError("Key number %i of `types` is not a tuple, but instead %s!" % (index, key.__class__.__name__))
            if len(key) != 2:
                raise TypeError("Key number %i of `types` is not length 2, but instead length %i!" % (index, len(key)))
            if not isinstance(key[0], str):
                raise TypeError("Item 0 of key number %i of `types` is not a str, but instead %s!" % (index, key[0].__class__.__name__))
            if not isinstance(key[1], type):
                raise TypeError("Item 1 of key \"%s\" of `types` is not a type, but instead %s!" % (key[0], key[1].__class__.__name__))
            if not (value is None or isinstance(value, ComparerSection.ComparerSection)):
                raise TypeError("Value of key \"%s\" of `types` is not a ComparerSection, but instead %s!" % (key, value.__class__.__name__))
        if not (self.normalizer is None or isinstance(self.normalizer, list)):
            raise TypeError("`normalizer` is not a list or None!")
        if isinstance(self.normalizer, list) and len(self.normalizer) == 0:
            raise TypeError("`normalizer` is empty!")
        if isinstance(self.normalizer, list) and not all(isinstance(item, Normalizer.Normalizer) for item in self.normalizer):
            raise TypeError("An item of `normalizer` is not a Normalizer!")
        if not isinstance(self.children_has_normalizer, bool):
            raise TypeError("`children_has_normalizer` is not a bool!")

    def check_type(self, key:str, value:d, trace:Trace.Trace) -> tuple[Trace.Trace,Exception]|None:
        if isinstance(key, D.Diff) or isinstance(value, D.Diff):
            raise TypeError("`check_all_types` was given data containing Diffs!")
        key_types:dict[str,list[type]] = {}
        # TODO: why is this code (below) in here
        for allowed_key, key_type in self.types:
            if allowed_key not in key_types:
                key_types[allowed_key] = [key_type]
            else:
                key_types[allowed_key].append(key_type)
        if key not in key_types:
            return (trace.copy(self.name, key), TypeError("Key, value %s: %s in %s excepted because key is not recognized!" % (CU.stringify(key), CU.stringify(value), self.name)))
        if type(value) not in key_types[key]:
            value_types_string = ", ".join(type_key.__name__ for type_key in key_types[key])
            return (trace.copy(self.name, key), TypeError("Key, value %s: %s in %s excepted because value is %s instead of [%s]!" % (CU.stringify(key), CU.stringify(value), self.name, value.__class__.__name__, value_types_string)))

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
