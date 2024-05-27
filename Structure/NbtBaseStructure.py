from typing import Iterable, Literal

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureSet as StructureSet
import Structure.StructureUtilities as SU
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
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a list", True, TypeVerifier.ListTypeVerifier(Normalizer.Normalizer, list, "a Normalizer", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("children_has_normalizers", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("children_tags", "a set", True, TypeVerifier.IterableTypeVerifier(str, set, "a str", "a set")),
    )

    def __init__(
            self,
            name:str,
            types:tuple[type,...]|None,
            endianness:Endianness.End,
            children_has_normalizer:bool,
            children_tags:set[str]
        ) -> None:
        super().__init__(name, name, children_has_normalizer, children_tags)

        self.types = (object,) if types is None else types
        self.endianness=endianness

        self.structure:Structure.Structure|dict[type,Structure.Structure|None]|None = None
        self.normalizer:list[Normalizer.Normalizer]|None = None

    def link_substructures(
        self,
        structure:Structure.Structure|dict[type,Structure.Structure|None],
        normalizer:list[Normalizer.Normalizer],
    ) -> None:
        self.structure = structure
        self.normalizer = normalizer

    def check_initialization_parameters(self) -> None:
        self.type_verifier.base_verify({
            "name": self.name,
            "structure": self.structure,
            "types": self.types,
            "endianness": self.endianness,
            "normalizer": self.normalizer,
            "children_has_normalizers": self.children_has_normalizer,
            "children_tags": self.children_tags,
        })

    def iter_structures(self) -> Iterable[Structure.Structure]:
        if self.structure is None: return []
        elif isinstance(self.structure, dict): return (substructure for substructure in self.structure.values() if substructure is not None)
        else: return [self.structure]

    def check_all_types(self, data: NbtTypes.TAG, environment:StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        output:list[Trace.ErrorTrace] = []
        if isinstance(data, D.Diff):
            raise TypeError("`check_all_types` was given data containing Diffs!")
        if not isinstance(data, self.types):
            item_types_string = ", ".join(type_key.__name__ for type_key in self.types)
            output.append(Trace.ErrorTrace(TypeError("Data %s in %s excepted is %s instead of [%s]!" % (SU.stringify(data), self.name, data.__class__.__name__, item_types_string)), self.name, None, data))
            return output
        structure, new_exceptions = self.choose_structure_flat("", type(data), data)
        for exception in new_exceptions: exception.add(self.name, None)
        output.extend(new_exceptions)
        if structure is not None:
            new_exceptions = structure.check_all_types(data, environment)
            for exception in new_exceptions: exception.add(self.name, None)
            output.extend(new_exceptions)
        return output

    def choose_structure_flat(self, key:Literal[""], value_type:type[NbtTypes.TAG], value:NbtTypes.TAG|None) -> tuple[Structure.Structure|None, list[Trace.ErrorTrace]]:
        if key != "":
            return None, [Trace.ErrorTrace(RuntimeError("Nbt root tag name at %s is not an empty string, but instead \"%s\"!" % (key)), self.name, key, value_type)]
        if isinstance(self.structure, dict):
            output = self.structure.get(value_type, Structure.StructureFailure.choose_structure_failure)
            if output is Structure.StructureFailure.choose_structure_failure:
                return None, [Trace.ErrorTrace(KeyError("Failed to get Structure at: %s" % (value_type)), self.name, key, value)]
            return output, []
        else:
            return self.structure, []

    def choose_structure(self, item:NbtTypes.TAG|D.Diff[NbtTypes.TAG,NbtTypes.TAG]) -> tuple[StructureSet.StructureSet,list[Trace.ErrorTrace]]:
        output:dict[D.DiffType,Structure.Structure|None] = {}
        exceptions:list[Trace.ErrorTrace] = []
        for item_iter, diff_type in D.iter_diff(item):
            if isinstance(self.structure, dict):
                structure = self.structure.get(type(item_iter), Structure.StructureFailure.choose_structure_failure)
                if structure is Structure.StructureFailure.choose_structure_failure:
                    exceptions.append(Trace.ErrorTrace(KeyError("Failed to get Structure at: %s" % (item_iter)), self.name, None, item))
                    continue
                output[diff_type] = structure
            else:
                output[diff_type] = self.structure
        return StructureSet.StructureSet(output), exceptions

    def normalize(self, data: NbtReader.NbtBytes, normalizer_dependencies: Normalizer.LocalNormalizerDependencies, version_number: int, environment:StructureEnvironment.StructureEnvironment) -> tuple[NbtTypes.TAG|None, list[Trace.ErrorTrace]]:
        try:
            data_parsed = NbtReader.unpack_bytes(data.open(), gzipped=False, endianness=self.endianness)[1]
        except Exception as e:
            return None, [Trace.ErrorTrace(e, self.name, None, data)]
        if not self.children_has_normalizer: return data_parsed, []
        assert self.normalizer is not None
        for normalizer in self.normalizer:
            try:
                normalizer(data_parsed, normalizer_dependencies, version_number)
            except Exception as e:
                return None, [Trace.ErrorTrace(e, self.name, None, data)]
        exceptions:list[Trace.ErrorTrace] = []
        structure, new_exceptions = self.choose_structure_flat("", type(data_parsed), data_parsed)
        for exception in new_exceptions: exception.add(self.name, None)
        exceptions.extend(new_exceptions)
        if structure is not None:
            normalize_output, new_exceptions = structure.normalize(data_parsed, normalizer_dependencies, version_number, environment)
            for exception in new_exceptions: exception.add(self.name, None)
            exceptions.extend(new_exceptions)
            if normalize_output is not None:
                data_parsed = normalize_output
        return data_parsed, exceptions

    def get_tag_paths(self, data: NbtTypes.TAG, tag: str, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath], list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        exceptions:list[Trace.ErrorTrace] = []
        structure, new_exceptions = self.choose_structure_flat("", type(data), data)
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
