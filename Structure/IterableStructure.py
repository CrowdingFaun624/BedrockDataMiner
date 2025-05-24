from types import EllipsisType
from typing import Any, Callable, Hashable, Mapping, Self, Sequence

import Structure.Container as Con
import Structure.DataPath as DataPath
import Structure.Delegate.Delegate as Delegate
import Structure.Difference as Diff
import Structure.IterableContainer as ICon
import Structure.Normalizer as Normalizer
import Structure.SimpleContainer as SCon
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureTag as StructureTag
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace


class IterableStructure[K:Hashable, V, D, KBO, KCO, VBO, VCO, BO, CO](Structure.Structure[
    D,
    ICon.ICon[Con.Con[K], Con.Con[V], D],
    ICon.IDon[Diff.Diff[Con.Don[K]], Diff.Diff[Con.Don[V]], D, Con.Con[K], Con.Con[V]],
    ICon.IDon[Diff.Diff[Con.Don[K]], Diff.Diff[Con.Don[V]], D, Con.Con[K], Con.Con[V]],
    BO, CO,
]):
    '''
    This type of Structure can act when the Domain's typestuff knows both how to iterate and how to set items of the data.
    '''

    __slots__ = (
        "delegate",
        "key_function",
        "key_types",
        "normalizers",
        "post_normalizers",
        "pre_normalized_types",
        "required_keys",
        "tags",
        "this_types",
    )

    def link_iterable_structure(
        self,
        delegate:Delegate.Delegate[ICon.ICon[Con.Con[K], Con.Con[V], D], ICon.IDon[Diff.Diff[Con.Don[K]], Diff.Diff[Con.Don[V]], D, Con.Con[K], Con.Con[V]], Self, BO, Any, CO, Any]|None,
        key_function:Callable[[K], str],
        key_types:tuple[type,...],
        normalizers:Sequence[Normalizer.Normalizer[D, D]],
        post_normalizers:Sequence[Normalizer.Normalizer[D, D]],
        pre_normalized_types:tuple[type,...],
        required_keys:set[str],
        tags:set[StructureTag.StructureTag],
        this_types:tuple[type,...],
    ) -> None:
        self.delegate = delegate
        self.key_function = key_function # function that turns K into str for access in `required_keys`, etc.
        self.key_types = key_types
        self.normalizers = normalizers
        self.post_normalizers = post_normalizers
        self.pre_normalized_types = pre_normalized_types
        self.required_keys = required_keys
        self.tags = tags
        self.this_types = this_types

    def get_key_structure(self, key:K, value:V, trace:Trace.Trace, environment:StructureEnvironment.PrinterEnvironment) -> Structure.Structure[K, Con.Con[K], Con.Don[K], Con.Don[K]|Diff.Diff[Con.Don[K]], KBO, KCO]|None:
        '''
        Returns a Structure that can act on the key of the Iterable of this Structure or None.
        '''
        ...

    def get_value_structure(self, key:K, value:V, trace:Trace.Trace, environment:StructureEnvironment.PrinterEnvironment) -> Structure.Structure[V, Con.Con[V], Con.Don[V], Con.Don[V]|Diff.Diff[Con.Don[V]], VBO, VCO]|None:
        '''
        Returns a Structure that can act on the value of the Iterable of this Structure or None.
        '''
        ...

    def get_key_structure_chain_end(self, key:Con.Con[K], value:Con.Con[V], trace:Trace.Trace, environment:StructureEnvironment.PrinterEnvironment) -> Structure.Structure|None:
        if (structure := self.get_key_structure(key.data, value.data, trace, environment)) is None:
            return None
        else:
            return structure.get_structure_chain_end(key, trace, environment)

    def get_value_structure_chain_end(self, key:Con.Con[K], value:Con.Con[V], trace:Trace.Trace, environment:StructureEnvironment.PrinterEnvironment) -> Structure.Structure|None:
        if (structure := self.get_value_structure(key.data, value.data, trace, environment)) is None:
            return None
        else:
            return structure.get_structure_chain_end(value, trace, environment)

    def get_value_types(self, key:K, value:V, trace:Trace.Trace, environment:StructureEnvironment.PrinterEnvironment) -> tuple[type,...]:
        '''
        Returns the types that this specific value can be.
        '''
        ...

    def get_value_tags(self, key:K, value:V, trace:Trace.Trace, environment:StructureEnvironment.PrinterEnvironment) -> set[StructureTag.StructureTag]|None:
        '''
        Returns the StructureTags associated with the given value.
        Return an empty set or None if there are no associated StructureTags.
        '''
        return None

    def normalize(self, data: D, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> D|EllipsisType:
        with trace.enter(self, self.name, data):
            if not isinstance(data, self.pre_normalized_types):
                trace.exception(Exceptions.StructureTypeError(self.pre_normalized_types, type(data), "Data", "(pre-normalized)"))
                return ...

            data, pre_data_identity_changed = self.normalizer_pass(self.normalizers, data, trace, environment)

            setitem_function = environment.domain.type_stuff.setitem_table.get(type(data))
            popitem_function = environment.domain.type_stuff.popitem_table.get(type(data))
            for key, value in environment.domain.type_stuff.iterate_data(data):
                key: K; value: V
                with trace.enter_key(key, value):
                    key_structure = self.get_key_structure(key, value, trace, environment)
                    value_structure = self.get_value_structure(key, value, trace, environment)
                    normalized_key = self.normalize_item(key, key_structure, trace, environment)
                    normalized_value = self.normalize_item(value, value_structure, trace, environment)
                    self.normalize_set_item(data, key, value, normalized_key, normalized_value, setitem_function, popitem_function, trace)

            data, post_data_identity_changed = self.normalizer_pass(self.post_normalizers, data, trace, environment)

            return data if pre_data_identity_changed or post_data_identity_changed else ...
        return ...

    def normalize_item[A](self, item:A, structure:Structure.Structure[A, Con.Con[A], Con.Don[A], Con.Don[A]|Diff.Diff[Con.Don[A]], Any, Any]|None, trace:Trace.Trace, environment:StructureEnvironment.PrinterEnvironment) -> A|None:
        if structure is not None and structure.children_has_normalizer:
            normalizer_output = structure.normalize(item, trace, environment)
            if normalizer_output is not ...:
                return normalizer_output
        return None

    def normalize_set_item(self, data:D, key:K, value:V, normalized_key:K|None, normalized_value:V|None, setitem_function:Callable[[D, K, V], None]|None, popitem_function:Callable[[D, K], V]|None, trace:Trace.Trace) -> None:
        if normalized_key is None and normalized_value is None:
            pass
        elif normalized_key is None and normalized_value is not None:
            if setitem_function is None:
                trace.exception(Exceptions.StructureNoManipulationFunctionError("setitem", type(data), "so values cannot be changed"))
            else:
                setitem_function(data, key, normalized_value)
        elif normalized_key is not None and normalized_value is None:
            if popitem_function is None or setitem_function is None:
                text = "popitem" if setitem_function is not None else ("setitem" if popitem_function is not None else "setitem or popitem")
                trace.exception(Exceptions.StructureNoManipulationFunctionError(text, type(data), "so keys cannot be changed"))
            else:
                popitem_function(data, key)
                setitem_function(data, normalized_key, value)
        elif normalized_key is not None and normalized_value is not None:
            if popitem_function is None or setitem_function is None:
                text = "popitem" if setitem_function is not None else ("setitem" if popitem_function is not None else "setitem or popitem")
                trace.exception(Exceptions.StructureNoManipulationFunctionError(text, type(data), "so keys cannot be changed"))
            else:
                popitem_function(data, key)
                setitem_function(data, normalized_key, normalized_value)

    def containerize(self, data: D, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> ICon.ICon[Con.Con[K], Con.Con[V], D]|EllipsisType:
        with trace.enter(self, self.name, data):
            containers:list[tuple[Con.Con[K], Con.Con[V]]] = []
            for key, value in environment.domain.type_stuff.iterate_data(data):
                with trace.enter_key(key, value):
                    key_structure = self.get_key_structure(key, value, trace, environment)
                    value_structure = self.get_value_structure(key, value, trace, environment)
                    key_container = self.containerize_item(key, key_structure, trace, environment)
                    value_container = self.containerize_item(value, value_structure, trace, environment)
                    if key_container is not ... and value_container is not ...:
                        containers.append((key_container, value_container))
            return ICon.icon_from_list(containers, data)
        return ...

    def containerize_item[A](self, item:A, structure:Structure.Structure[A, Con.Con[A], Con.Don[A], Con.Don[A]|Diff.Diff[Con.Don[A]], Any, Any]|None, trace:Trace.Trace, environment:StructureEnvironment.PrinterEnvironment) -> Con.Con[A]|EllipsisType:
        if structure is None:
            return SCon.SCon(item, environment.domain)
        else:
            return structure.containerize(item, trace, environment)

    def diffize(
        self,
        data: ICon.ICon[Con.Con[K], Con.Con[V], D],
        bundle: tuple[int, ...],
        trace: Trace.Trace,
        environment: StructureEnvironment.ComparisonEnvironment,
    ) -> Mapping[tuple[int, ...], ICon.IDon[Diff.Diff[Con.Don[K]], Diff.Diff[Con.Don[V]], D, Con.Con[K], Con.Con[V]]] | EllipsisType:
        # this method was very annoying.
        with trace.enter(self, self.name, data):
            diffed_items:list[Mapping[tuple[int,...], tuple[Diff.Diff[Con.Don[K]], Diff.Diff[Con.Don[V]]]]] = []
            current_length:int = 0
            for undiffed_key, undiffed_value in data.items(): # weird names because of lambda expressions.
                with trace.enter_key(undiffed_key, undiffed_value):
                    current_length += 1
                    diffed_key = self.diffize_item(undiffed_key, bundle, lambda branch: self.get_key_structure_chain_end(undiffed_key, undiffed_value, trace, environment[branch]), trace, environment)
                    diffed_value = self.diffize_item(undiffed_value, bundle, lambda branch: self.get_value_structure_chain_end(undiffed_key, undiffed_value, trace, environment[branch]), trace, environment)
                    diffed_items.append(self.combine_key_value(diffed_key, diffed_value, bundle))
            if current_length == 0: # If `data` is an empty ICon, then the above for loop will do nothing, leading eventually to a Diff with no items (bad).
                return {bundle: ICon.idon_from_list([], {branch: data for branch in bundle})}
            else:
                return {local_bundle: ICon.idon_from_list(items, {branch: data for branch in local_bundle}) for local_bundle, items in self.combine_bundles(diffed_items, bundle).items()}
        return ...

    def diffize_item[A](
        self,
        item:Con.Con[A],
        bundle:tuple[int,...],
        structure_function:Callable[[int], Structure.Structure[A, Con.Con[A], Con.Don[A], Con.Don[A]|Diff.Diff[Con.Don[A]], Any, Any]|None],
        trace:Trace.Trace,
        environment:StructureEnvironment.ComparisonEnvironment,
    ) -> dict[tuple[int,...], Con.Don[A]]:
        structures = [(branch, structure := structure_function(branch)) for branch in bundle]
        structure_bundles:list[tuple[tuple[int,...], Structure.Structure[A, Con.Con[A], Con.Don[A], Con.Don[A]|Diff.Diff[Con.Don[A]], Any, Any]|None]] = []
        current_bundle:list[int] = []
        current_structure:Structure.Structure[A, Con.Con[A], Con.Don[A], Con.Don[A]|Diff.Diff[Con.Don[A]], BO, CO]|None|EllipsisType = ...
        for branch, structure in structures:
            if current_structure is ... or structure is current_structure:
                current_bundle.append(branch)
            else:
                structure_bundles.append((tuple(current_bundle), current_structure))
                current_bundle = [branch]
            current_structure = structure
        assert current_structure is not ...
        structure_bundles.append((tuple(current_bundle), current_structure))
        output:dict[tuple[int,...], Con.Don[A]] = {}
        for local_bundle, structure in structure_bundles:
            if structure is None:
                output[local_bundle] = item.as_don(local_bundle)
            else:
                diffize_output = structure.diffize(item, local_bundle, trace, environment)
                if diffize_output is ...:
                    continue
                output.update(diffize_output)
        return output

    def combine_bundles[A](self, data:list[Mapping[tuple[int,...], A]], top_bundle:tuple[int,...]) -> Mapping[tuple[int,...], list[A]]:
        bundle_ends:set[int] = {bundle[-1] for item_diff in data for bundle in item_diff}
        output:dict[tuple[int,...], list[A]] = {}
        bundle_map:dict[int,tuple[int,...]] = {}
        current_bundle:list[int] = []
        for branch in top_bundle:
            current_bundle.append(branch)
            if branch in bundle_ends:
                bundle_tuple = tuple(current_bundle)
                bundle_map.update((branch, bundle_tuple) for branch in bundle_tuple)
                output[bundle_tuple] = []
        for item_diff in data:
            for bundle, item in item_diff.items():
                for branch in bundle:
                    if branch in bundle_ends:
                        output[bundle_map[branch]].append(item)
        return output

    def combine_key_value(self, key_diff:Mapping[tuple[int,...], Con.Don[K]], value_diff:Mapping[tuple[int,...], Con.Don[V]], top_bundle:tuple[int,...]) -> Mapping[tuple[int,...], tuple[Diff.Diff[Con.Don[K]], Diff.Diff[Con.Don[V]]]]:
        bundle_ends:set[int] = {bundle[-1] for item_diff in (key_diff, value_diff) for bundle in item_diff}
        output:dict[tuple[int,...], tuple[dict[tuple[int,...], Con.Don[K]], dict[tuple[int,...], Con.Don[V]]]] = {} # lists are one-item (if not one-item, broken; help)
        bundle_map:dict[int,tuple[int,...]] = {}
        current_bundle:list[int] = []
        for branch in top_bundle:
            current_bundle.append(branch)
            if branch in bundle_ends:
                bundle_tuple = tuple(current_bundle)
                bundle_map.update((branch, bundle_tuple) for branch in bundle_tuple)
                output[bundle_tuple] = ({}, {})
        for bundle, key in key_diff.items():
            for branch in bundle:
                if branch in bundle_ends:
                    output[bundle_map[branch]][0][bundle] = key
        for bundle, value in value_diff.items():
            for branch in bundle:
                if branch in bundle_ends:
                    output[bundle_map[branch]][1][bundle] = value
        return {bundle: (Diff.Diff(key_list, False), Diff.Diff(value_list, False)) for bundle, (key_list, value_list) in output.items()}

    def type_check(self, data: ICon.ICon[Con.Con[K], Con.Con[V], D], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> None:
        with trace.enter(self, self.name, data):
            self.type_check_item(data.data, self.this_types, "Data", trace)
            required_keys:set[str] = self.required_keys.copy()
            for key, value in data.items():
                with trace.enter_key(key, value):
                    value_types = self.get_value_types(key.data, value.data, trace, environment)
                    self.type_check_item(key.data, self.key_types, "Key", trace)
                    self.type_check_item(value.data, value_types, "Value", trace)
                    required_keys.discard(self.key_function(key.data))
            if len(required_keys) != 0:
                trace.exception(Exceptions.StructureRequiredKeyMissingError(self, key))

    def type_check_item(self, item:object, types:tuple[type,...], label:str, trace:Trace.Trace) -> None:
        if not isinstance(item, types):
            trace.exception(Exceptions.StructureTypeError(types, type(item), label))

    def get_tag_paths(self, data: ICon.ICon[Con.Con[K], Con.Con[V], D], tag:StructureTag.StructureTag, data_path: DataPath.DataPath, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> Sequence[DataPath.DataPath]:
        with trace.enter(self, self.name, data):
            if tag not in self.children_tags:
                return ()
            output:list[DataPath.DataPath] = []
            if tag in self.tags:
                output.extend(data_path.copy(key).embed(value) for key, value in data.items())
            for key, value in data.items():
                with trace.enter_key(key, value):
                    key_structure = self.get_key_structure(key.data, value.data, trace, environment)
                    value_structure = self.get_value_structure(key.data, value.data, trace, environment)
                    if key_structure is not None:
                        output.extend(key_structure.get_tag_paths(key, tag, data_path, trace, environment))
                    if value_structure is not None:
                        output.extend(value_structure.get_tag_paths(value, tag, data_path, trace, environment))
            return output
        return () # error occurred

    def get_referenced_files(self, data: ICon.ICon[Con.Con[K], Con.Con[V], D], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> set[int]:
        with trace.enter(self, self.name, data):
            output:set[int] = set()
            if not self.children_has_garbage_collection: return set()
            for key, value in data.items():
                with trace.enter_key(key, value):
                    key_structure = self.get_key_structure(key.data, value.data, trace, environment)
                    value_structure = self.get_value_structure(key.data, value.data, trace, environment)
                    if key_structure is not None:
                        output.update(key_structure.get_referenced_files(key, trace, environment))
                    if value_structure is not None:
                        output.update(value_structure.get_referenced_files(value, trace, environment))
            return output
        return set()

    def print_branch(self, data: ICon.ICon[Con.Con[K], Con.Con[V], D], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> BO|EllipsisType:
        with trace.enter(self, self.name, data):
            if self.delegate is None:
                raise Exceptions.AttributeNoneError("delegate", self)
            return self.delegate.print_branch(data, trace, environment)
        return ...

    def print_comparison(self, data: ICon.IDon[Diff.Diff[Con.Don[K]], Diff.Diff[Con.Don[V]], D, Con.Con[K], Con.Con[V]], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> CO|EllipsisType:
        with trace.enter(self, self.name, data):
            if self.delegate is None:
                raise Exceptions.AttributeNoneError("delegate", self)
            return self.delegate.print_comparison(data, trace, environment)
        return ...

    # the below methods are utility methods for use in multiple subclasses.

    def get_key_similarity(self, key1:Con.Con[K], key2:Con.Con[K], value1:Con.Con[V], value2:Con.Con[V], branch1:int, branch2:int, trace:Trace.Trace, environment:StructureEnvironment.ComparisonEnvironment) -> tuple[float, bool]:
        if key1 is key2 or key1 == key2:
            return 1.0, True

        structure1 = self.get_key_structure(key1.data, value1.data, trace, (environment1 := environment[branch1]))
        if structure1 is None:
            return float(is_similar := (key1 is key2 or key1 == key2)), is_similar
        structure2 = self.get_key_structure(key2.data, value2.data, trace, (environment2 := environment[branch2]))
        if structure1 is not structure2 or structure2 is None:
            return float(is_similar := (key1 is key2 or key1 == key2)), is_similar

        structure1_chain_end = structure1.get_structure_chain_end(key1, trace, environment1)
        if structure1_chain_end is None:
            return float(is_similar := (key1 is key2 or key1 == key2)), is_similar
        structure2_chain_end = structure2.get_structure_chain_end(key2, trace, environment2)
        if structure1_chain_end is not structure2_chain_end:
            return float(is_similar := (key1 is key2 or key1 == key2)), is_similar
        return structure1.get_similarity(key1, key2, branch1, branch2, trace, environment)

    def get_value_similarity(self, key1:Con.Con[K], key2:Con.Con[K], value1:Con.Con[V], value2:Con.Con[V], branch1:int, branch2:int, trace:Trace.Trace, environment:StructureEnvironment.ComparisonEnvironment) -> tuple[float, bool]:
        if value1 is value2 or value1 == value2:
            return 1.0, True

        structure1 = self.get_value_structure(key1.data, value1.data, trace, (environment1 := environment[branch1]))
        if structure1 is None:
            return float(is_similar := (value1 is value2 or value1 == value2)), is_similar
        structure2 = self.get_value_structure(key2.data, value2.data, trace, (environment2 := environment[branch2]))
        if structure1 is not structure2 or structure2 is None:
            return float(is_similar := (value1 is value2 or value1 == value2)), is_similar

        structure1_chain_end = structure1.get_structure_chain_end(value1, trace, environment1)
        if structure1_chain_end is None:
            return float(is_similar := (value1 is value2 or value1 == value2)), is_similar
        structure2_chain_end = structure2.get_structure_chain_end(value2, trace, environment2)
        if structure1_chain_end is not structure2_chain_end:
            return float(is_similar := (value1 is value2 or value1 == value2)), is_similar
        return structure1.get_similarity(value1, value2, branch1, branch2, trace, environment)

    def assemble_output(
        self,
        cumulative_items:list[tuple[list[tuple[list[int], Con.Con[K]]], list[tuple[list[int], Con.Con[V]]]]],
        trace:Trace.Trace,
        environment:StructureEnvironment.ComparisonEnvironment,
    ) -> tuple[list[tuple[Diff.Diff[Con.Don[K]], Diff.Diff[Con.Don[V]]]], bool]:
        output:list[tuple[Diff.Diff[Con.Don[K]], Diff.Diff[Con.Don[V]]]] = []
        internal_changes = False
        for key_diff, value_diff in cumulative_items:
            simple_key_map = {branch: key for bundle, key in key_diff for branch in bundle}
            simple_value_map = {branch: value for bundle, value in value_diff for branch in bundle}
            key, key_internal_changes = self.get_item_diff(key_diff, lambda key, branch: self.get_key_structure_chain_end(key, simple_value_map[branch], trace, environment[branch]), trace, environment)
            value, value_internal_changes = self.get_item_diff(value_diff, lambda value, branch: self.get_value_structure_chain_end(simple_key_map[branch], value, trace, environment[branch]), trace, environment)
            internal_changes = internal_changes or value_internal_changes or key_internal_changes
            output.append((key, value))
        return output, internal_changes

    def get_item_diff[A](
        self,
        item_diff:list[tuple[list[int], Con.Con[A]]],
        structure_function:Callable[[Con.Con[A], int],Structure.Structure[A, Con.Con[A], Con.Don[A], Con.Don[A]|Diff.Diff[Con.Don[A]], Any, Any]|None],
        trace:Trace.Trace,
        environment:StructureEnvironment.ComparisonEnvironment,
    ) -> tuple[Diff.Diff[Con.Don[A]], bool]: # Diff and if the Diff has any internal changes.
        structure_bundles:list[tuple[Structure.Structure[A, Con.Con[A], Con.Don[A], Con.Don[A]|Diff.Diff[Con.Don[A]], Any, Any]|None, list[tuple[tuple[int,...], Con.Con[A]]]]] = []
        for bundle, item in item_diff:
            previous_structure, previous_bundles = structure_bundles[-1] if len(structure_bundles) != 0 else (..., [])
            structure = structure_function(item, bundle[-1])
            if previous_structure is structure:
                # cannot occur if `previous_structure` is ...; therefore, the problem with `previous_bundles` not being inside anything DNE.
                previous_bundles.append((tuple(bundle), item))
            else:
                structure_bundles.append((structure, [(tuple(bundle), item)]))
        internal_changes:bool = False
        advanced_diff:dict[tuple[int,...], Con.Don[A]] = {}
        for structure, bundles in structure_bundles:
            if structure is None:
                advanced_diff.update((bundle, item.as_don(bundle)) for bundle, item in bundles)
            elif len(comparison_tuple := tuple((branch, item) for bundle, item in bundles for branch in bundle)) == 1:
                comparison_mapping = structure.diffize(comparison_tuple[0][1], (comparison_tuple[0][0],), trace, environment)
                if comparison_mapping is ...:
                    continue
                advanced_diff.update(comparison_mapping)
            else:
                # second item is not factored into `compare`, but it indicates that there are internal changes.
                comparison_output, any_changes, any_internal_changes = structure.compare(comparison_tuple, trace, environment)
                internal_changes = internal_changes or any_internal_changes
                if comparison_output is ...:
                    continue
                elif isinstance(comparison_output, Diff.Diff):
                    advanced_diff.update(comparison_output.items)
                else:
                    # if comparison_output is an IDon, then any change becomes an internal change.
                    internal_changes = internal_changes or any_changes
                    advanced_diff[tuple(branch for bundle, _ in bundles for branch in bundle)] = comparison_output
        return Diff.Diff(advanced_diff, internal_changes), internal_changes
