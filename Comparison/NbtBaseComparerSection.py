from typing import Literal

import Comparison.ComparerSection as ComparerSection
import Comparison.ComparerSet as ComparerSet
import Comparison.ComparisonUtilities as CU
import Comparison.Difference as D
import Comparison.Normalizer as Normalizer
import Comparison.Trace as Trace
import Utilities.Nbt.Endianness as Endianness
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.Nbt.NbtTypes as NbtTypes

class NbtBaseComparerSection(ComparerSection.ComparerSection[NbtTypes.TAG]):

    def __init__(
            self,
            name:str,
            comparer:ComparerSection.ComparerSection|dict[type,ComparerSection.ComparerSection|None]|None,
            types:tuple[type,...]|None,
            endianness:Endianness.End,
            normalizers:list[Normalizer.Normalizer]|None=None,
            children_has_normalizers:bool=False,
        ) -> None:
        self.name = name
        self.comparer = comparer
        self.types = (object,) if types is None else types
        self.normalizers = normalizers
        self.children_has_normalizer = children_has_normalizers
        self.endianness=endianness
        self.check_initialization_parameters()

    def check_initialization_parameters(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("`name` is not a str!")
        if not (self.comparer is None or isinstance(self.comparer, (ComparerSection.ComparerSection, dict))):
            raise TypeError("`comparer` is not a ComparerSection, NoneType, or dict, but instead a %s!" % (self.comparer.__class__.__name__))
        if isinstance(self.comparer, dict):
            for comparer_index, (comparer_key, comparer_value) in enumerate(self.comparer.items()):
                if not isinstance(comparer_key, type):
                    raise TypeError("Key number %i of `comparer` is not a type, but instead a %s!" % (comparer_index, comparer_key.__class__.__name__))
                if not (comparer_value is None or isinstance(comparer_value, ComparerSection.ComparerSection)):
                    raise TypeError("Key \"%s\" of `comparer` is not a ComparerSection or None, but instead a %s!" % (comparer_key.__name__, comparer_value.__class__.__name__))
        if not isinstance(self.types, tuple) and self.types is not None:
            raise TypeError("`types` is not a tuple or None, but instead a %s!" % (self.types.__class__.__name__))
        if isinstance(self.types, tuple) and not all(isinstance(item, (type)) for item in self.types):
            raise TypeError("An item of `types` is not a type!")
        if not isinstance(self.endianness, Endianness.End):
            raise TypeError("`endianness` is not an End!")

    def check_all_types(self, data: NbtTypes.TAG, trace: Trace.Trace) -> list[tuple[Trace.Trace, Exception]]:
        if isinstance(data, D.Diff):
            raise TypeError("`check_all_types` was given data containing Diffs!")
        if not isinstance(data, self.types):
            item_types_string = ", ".join(type_key.__name__ for type_key in self.types)
            return [(trace.copy(self.name), TypeError("Data %s in %s excepted is %s instead of [%s]!" % (CU.stringify(data), self.name, data.__class__.__name__, item_types_string)))]
        comparer = self.choose_comparer_flat("", type(data), trace)
        if comparer is not None:
            return comparer.check_all_types(data, trace.copy(self.name))
        return []

    def choose_comparer_flat(self, key:Literal[""], value:type[NbtTypes.TAG], trace:Trace.Trace) -> ComparerSection.ComparerSection|None:
        if key != "":
            raise RuntimeError("Nbt root tag name at %s is not an empty string, but instead \"%s\"!" % key)
        if isinstance(self.comparer, dict):
            exception = None
            try:
                return self.comparer[value]
            except Exception as e:
                exception = e
                exception.args = tuple(list(exception.args) + ["Failed to get comparer at %s: %s" % (trace, value)])
            if exception is not None:
                raise exception
        else:
            return self.comparer

    def choose_comparer(self, item:NbtTypes.TAG|D.Diff[NbtTypes.TAG,NbtTypes.TAG], trace:Trace.Trace) -> ComparerSet.ComparerSet:
        output:dict[D.DiffType,ComparerSection.ComparerSection|None] = {}
        for item_iter, diff_type in D.iter_diff(item):
            if isinstance(self.comparer, dict):
                exception = None
                try:
                    output[diff_type] = self.comparer[type(item_iter)]
                except Exception as e:
                    exception = e
                    exception.args = tuple(list(exception.args) + ["Failed to get comparer at %s: %s" % (trace, item_iter)])
                if exception is not None:
                    raise exception
            else:
                output[diff_type] = self.comparer
        return ComparerSet.ComparerSet(output)

    def normalize(self, data: NbtReader.NbtBytes, normalizer_dependencies: Normalizer.LocalNormalizerDependencies, version_number: int, trace: Trace.Trace) -> NbtTypes.TAG:
        exception = None
        try:
            data_parsed = NbtReader.unpack_bytes(data.value, gzipped=False, endianness=self.endianness)[1]
        except Exception as e:
            raise RuntimeError("Failed to parse nbt at %s!" % (trace))
        if exception is not None:
            raise exception # type: ignore

        if not self.children_has_normalizer: return data_parsed
        if self.normalizer is not None:
            for normalizer in self.normalizer:
                normalizer(data_parsed, normalizer_dependencies, trace, version_number)
        try:
            comparer = self.choose_comparer_flat("", type(data_parsed), trace)
        except Exception:
            # it hasn't been type checked yet, so something could except
            return data_parsed
        if comparer is not None:
            normalize_output = comparer.normalize(data_parsed, normalizer_dependencies, version_number, trace.copy(self.name))
            if normalize_output is not None:
                data_parsed = normalize_output
        return data_parsed

    def compare(self, data1: NbtTypes.TAG, data2: NbtTypes.TAG, trace: Trace.Trace) -> tuple[NbtTypes.TAG|D.Diff[NbtTypes.TAG, NbtTypes.TAG], list[tuple[Trace.Trace, Exception]]]:
        comparer_set = self.choose_comparer(D.Diff(data1, data2), trace)
        return comparer_set.compare(data1, data2, trace)

    def print_text(self, data: NbtTypes.TAG, trace: Trace.Trace) -> list[str]:
        return self.choose_comparer(data, trace).print_text(D.DiffType.not_diff, data, trace.copy(self.name))

    def compare_text(self, data:NbtTypes.TAG|D.Diff[NbtTypes.TAG,NbtTypes.TAG], trace: Trace.Trace) -> tuple[list[str], bool]:
        comparer_set = self.choose_comparer(data, trace)
        if isinstance(data, D.Diff):
            output:list[str] = []
            match data.change_type:
                case D.ChangeType.addition:
                    self.print_single(None, data.new, "Added", output, comparer_set[D.DiffType.new], trace)
                case D.ChangeType.change:
                    self.print_double(None, data.old, data.new, "Changed", output, comparer_set, trace)
                case D.ChangeType.removal:
                    self.print_single(None, data.old, "Removed", output, comparer_set[D.DiffType.old], trace)
            return output, True
        else:
            return comparer_set.compare_text(D.DiffType.not_diff, data, trace.copy(self.name))
