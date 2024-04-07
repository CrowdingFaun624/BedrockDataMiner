from typing import Literal

import Structure.Structure as Structure
import Structure.StructureSet as StructureSet
import Structure.StructureUtilities as SU
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Trace as Trace
import Utilities.Nbt.Endianness as Endianness
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.Nbt.NbtTypes as NbtTypes
import Utilities.TypeVerifier as TypeVerifier

class NbtBaseStructure(Structure.Structure[NbtTypes.TAG]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("structure", "a Structure, a dict, or None", True, TypeVerifier.UnionTypeVerifier(
            "a Structure, a dict, or None",
            Structure.Structure,
            type(None),
            TypeVerifier.DictTypeVerifier(dict, type, (Structure.Structure, type(None)), "a dict", "a type", "a Structure or None"),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a tuple or None", True, TypeVerifier.UnionTypeVerifier(
            "a tuple or None",
            type(None),
            TypeVerifier.ListTypeVerifier(type, tuple, "a type", "a tuple"),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("endianness", "an End", True, Endianness.End),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a list or None", True, TypeVerifier.UnionTypeVerifier(
            "a list or None",
            type(None),
            TypeVerifier.ListTypeVerifier(Normalizer.Normalizer, list, "a Normalizer", "a list"),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("children_has_normalizers", "a bool", True, bool),
    )

    def __init__(
            self,
            name:str,
            structure:Structure.Structure|dict[type,Structure.Structure|None]|None,
            types:tuple[type,...]|None,
            endianness:Endianness.End,
            normalizer:list[Normalizer.Normalizer]|None,
            children_has_normalizer:bool,
        ) -> None:
        self.name = name
        self.structure = structure
        self.types = (object,) if types is None else types
        self.normalizer = normalizer
        self.children_has_normalizer = children_has_normalizer
        self.endianness=endianness
        self.check_initialization_parameters()

    def check_initialization_parameters(self) -> None:
        self.type_verifier.base_verify({
            "name": self.name,
            "structure": self.structure,
            "types": self.types,
            "endianness": self.endianness,
            "normalizer": self.normalizer,
            "children_has_normalizers": self.children_has_normalizer
        })

    def check_all_types(self, data: NbtTypes.TAG, trace: Trace.Trace) -> list[tuple[Trace.Trace, Exception]]:
        if isinstance(data, D.Diff):
            raise TypeError("`check_all_types` was given data containing Diffs!")
        if not isinstance(data, self.types):
            item_types_string = ", ".join(type_key.__name__ for type_key in self.types)
            return [(trace.copy(self.name), TypeError("Data %s in %s excepted is %s instead of [%s]!" % (SU.stringify(data), self.name, data.__class__.__name__, item_types_string)))]
        structure = self.choose_structure_flat("", type(data), trace)
        if structure is not None:
            return structure.check_all_types(data, trace.copy(self.name))
        return []

    def choose_structure_flat(self, key:Literal[""], value:type[NbtTypes.TAG], trace:Trace.Trace) -> Structure.Structure|None:
        if key != "":
            raise RuntimeError("Nbt root tag name at %s is not an empty string, but instead \"%s\"!" % key)
        if isinstance(self.structure, dict):
            exception = None
            try:
                return self.structure[value]
            except Exception as e:
                exception = e
                exception.args = tuple(list(exception.args) + ["Failed to get Structure at %s: %s" % (trace, value)])
            if exception is not None:
                raise exception
        else:
            return self.structure

    def choose_structure(self, item:NbtTypes.TAG|D.Diff[NbtTypes.TAG,NbtTypes.TAG], trace:Trace.Trace) -> StructureSet.StructureSet:
        output:dict[D.DiffType,Structure.Structure|None] = {}
        for item_iter, diff_type in D.iter_diff(item):
            if isinstance(self.structure, dict):
                exception = None
                try:
                    output[diff_type] = self.structure[type(item_iter)]
                except Exception as e:
                    exception = e
                    exception.args = tuple(list(exception.args) + ["Failed to get Structure at %s: %s" % (trace, item_iter)])
                if exception is not None:
                    raise exception
            else:
                output[diff_type] = self.structure
        return StructureSet.StructureSet(output)

    def normalize(self, data: NbtReader.NbtBytes, normalizer_dependencies: Normalizer.LocalNormalizerDependencies, version_number: int, trace: Trace.Trace) -> NbtTypes.TAG:
        try:
            data_parsed = NbtReader.unpack_bytes(data.value, gzipped=False, endianness=self.endianness)[1]
        except Exception:
            raise RuntimeError("Failed to parse nbt at %s!" % (trace))

        if not self.children_has_normalizer: return data_parsed
        if self.normalizer is not None:
            for normalizer in self.normalizer:
                normalizer(data_parsed, normalizer_dependencies, trace, version_number)
        try:
            structure = self.choose_structure_flat("", type(data_parsed), trace)
        except Exception:
            # it hasn't been type checked yet, so something could except
            return data_parsed
        if structure is not None:
            normalize_output = structure.normalize(data_parsed, normalizer_dependencies, version_number, trace.copy(self.name))
            if normalize_output is not None:
                data_parsed = normalize_output
        return data_parsed

    def compare(self, data1: NbtTypes.TAG, data2: NbtTypes.TAG, trace: Trace.Trace) -> tuple[NbtTypes.TAG|D.Diff[NbtTypes.TAG, NbtTypes.TAG], list[tuple[Trace.Trace, Exception]]]:
        structure_set = self.choose_structure(D.Diff(data1, data2), trace)
        return structure_set.compare(data1, data2, trace)

    def print_text(self, data: NbtTypes.TAG, trace: Trace.Trace) -> list[SU.Line]:
        return self.choose_structure(data, trace).print_text(D.DiffType.not_diff, data, trace.copy(self.name))

    def compare_text(self, data:NbtTypes.TAG|D.Diff[NbtTypes.TAG,NbtTypes.TAG], trace: Trace.Trace) -> tuple[list[SU.Line], bool]:
        structure_set = self.choose_structure(data, trace)
        if isinstance(data, D.Diff):
            output:list[SU.Line] = []
            match data.change_type:
                case D.ChangeType.addition:
                    self.print_single(None, data.new, "Added", output, structure_set[D.DiffType.new], trace)
                case D.ChangeType.change:
                    self.print_double(None, data.old, data.new, "Changed", output, structure_set, trace)
                case D.ChangeType.removal:
                    self.print_single(None, data.old, "Removed", output, structure_set[D.DiffType.old], trace)
            return output, True
        else:
            return structure_set.compare_text(D.DiffType.not_diff, data, trace.copy(self.name))
