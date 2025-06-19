from types import EllipsisType
from typing import Any, Callable, Hashable, Mapping, Self, Sequence

from ordered_set import OrderedSet

from Structure.Container import Con, Don
from Structure.DataPath import DataPath
from Structure.Delegate.Delegate import Delegate
from Structure.Difference import Diff
from Structure.IterableContainer import ICon, IDon, icon_from_list, idon_from_list
from Structure.Normalizer import Normalizer
from Structure.SimpleContainer import SCon
from Structure.Structure import Structure
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Structure.StructureTag import StructureTag
from Structure.Uses import NonEmptyUse, Region, StructureUse, TypeUse, UsageTracker, Use
from Utilities.Exceptions import (
    AttributeNoneError,
    StructureNoManipulationFunctionError,
    StructureRequiredKeyMissingError,
    StructureTypeError,
)
from Utilities.Trace import Trace


class IterableStructure[K:Hashable, V, D, KBO, KCO, VBO, VCO, BO, CO](Structure[
    D,
    ICon[Con[K], Con[V], D],
    IDon[Diff[Don[K]], Diff[Don[V]], D, Con[K], Con[V]],
    IDon[Diff[Don[K]], Diff[Don[V]], D, Con[K], Con[V]],
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
        delegate:Delegate[ICon[Con[K], Con[V], D], IDon[Diff[Don[K]], Diff[Don[V]], D, Con[K], Con[V]], Self, BO, Any, CO, Any]|None,
        key_function:Callable[[K], str],
        key_types:tuple[type,...],
        normalizers:Sequence[Normalizer],
        post_normalizers:Sequence[Normalizer],
        pre_normalized_types:tuple[type,...],
        required_keys:set[str],
        tags:set[StructureTag],
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

    def get_key_structure(self, key:K, value:V, trace:Trace, environment:PrinterEnvironment) -> Structure[K, Con[K], Don[K], Don[K]|Diff[Don[K]], KBO, KCO]|None:
        '''
        Returns a Structure that can act on the key of the Iterable of this Structure or None.
        '''
        ...

    def get_value_structure(self, key:K, value:V, trace:Trace, environment:PrinterEnvironment) -> Structure[V, Con[V], Don[V], Don[V]|Diff[Don[V]], VBO, VCO]|None:
        '''
        Returns a Structure that can act on the value of the Iterable of this Structure or None.
        '''
        ...

    def get_key_structure_chain_end(self, key:Con[K], value:Con[V], trace:Trace, environment:PrinterEnvironment) -> Structure|None:
        if (structure := self.get_key_structure(key.data, value.data, trace, environment)) is None:
            return None
        else:
            return structure.get_structure_chain_end(key, trace, environment)

    def get_value_structure_chain_end(self, key:Con[K], value:Con[V], trace:Trace, environment:PrinterEnvironment) -> Structure|None:
        if (structure := self.get_value_structure(key.data, value.data, trace, environment)) is None:
            return None
        else:
            return structure.get_structure_chain_end(value, trace, environment)

    def get_value_types(self, key:K, value:V, trace:Trace, environment:PrinterEnvironment) -> tuple[type,...]:
        '''
        Returns the types that this specific value can be.
        '''
        ...

    def get_value_tags(self, key:K, value:V, trace:Trace, environment:PrinterEnvironment) -> set[StructureTag]|None:
        '''
        Returns the StructureTags associated with the given value.
        Return an empty set or None if there are no associated StructureTags.
        '''
        return None

    def normalize(self, data: D, trace: Trace, environment: PrinterEnvironment) -> D|EllipsisType:
        with trace.enter(self, self.name, data):
            if not isinstance(data, self.pre_normalized_types):
                trace.exception(StructureTypeError(self.pre_normalized_types, type(data), "Data", "(pre-normalized)"))
                return ...

            data, pre_data_identity_changed = self.normalizer_pass(self.normalizers, data, trace, environment)

            if not isinstance(data, self.this_types):
                trace.exception(StructureTypeError(self.this_types, type(data), "Data"))
                return ...

            setitem_function = environment.domain.type_stuff.setitem_table.get(type(data))
            popitem_function = environment.domain.type_stuff.popitem_table.get(type(data))
            for key, value in list(environment.domain.type_stuff.iterate_data(data)): # wrapped with list because of modifications to iterator.
                key: K; value: V
                with trace.enter_key(key, value):
                    key_structure = self.get_key_structure(key, value, trace, environment)
                    value_structure = self.get_value_structure(key, value, trace, environment)
                    normalized_key = self.normalize_item(key, key_structure, trace, environment)
                    normalized_value = self.normalize_item(value, value_structure, trace, environment)
                    self.normalize_set_item(data, key, value, normalized_key, normalized_value, setitem_function, popitem_function, trace)

            data, post_data_identity_changed = self.normalizer_pass(self.post_normalizers, data, trace, environment)

            if not isinstance(data, self.this_types):
                trace.exception(StructureTypeError(self.this_types, type(data), "Data", "(post-normalized)"))
                return ...

            return data if pre_data_identity_changed or post_data_identity_changed else ...
        return ...

    def normalize_item[A](self, item:A, structure:Structure[A, Con[A], Don[A], Don[A]|Diff[Don[A]], Any, Any]|None, trace:Trace, environment:PrinterEnvironment) -> A|None:
        if structure is not None and structure.children_has_normalizer:
            normalizer_output = structure.normalize(item, trace, environment)
            if normalizer_output is not ...:
                return normalizer_output
        return None

    def normalize_set_item(self, data:D, key:K, value:V, normalized_key:K|None, normalized_value:V|None, setitem_function:Callable[[D, K, V], None]|None, popitem_function:Callable[[D, K], V]|None, trace:Trace) -> None:
        if normalized_key is None and normalized_value is None:
            pass
        elif normalized_key is None and normalized_value is not None:
            if setitem_function is None:
                trace.exception(StructureNoManipulationFunctionError("setitem", type(data), "so values cannot be changed"))
            else:
                setitem_function(data, key, normalized_value)
        elif normalized_key is not None and normalized_value is None:
            if popitem_function is None or setitem_function is None:
                text = "popitem" if setitem_function is not None else ("setitem" if popitem_function is not None else "setitem or popitem")
                trace.exception(StructureNoManipulationFunctionError(text, type(data), "so keys cannot be changed"))
            else:
                popitem_function(data, key)
                setitem_function(data, normalized_key, value)
        elif normalized_key is not None and normalized_value is not None:
            if popitem_function is None or setitem_function is None:
                text = "popitem" if setitem_function is not None else ("setitem" if popitem_function is not None else "setitem or popitem")
                trace.exception(StructureNoManipulationFunctionError(text, type(data), "so keys cannot be changed"))
            else:
                popitem_function(data, key)
                setitem_function(data, normalized_key, normalized_value)

    def containerize(self, data: D, trace: Trace, environment: PrinterEnvironment) -> ICon[Con[K], Con[V], D]|EllipsisType:
        with trace.enter(self, self.name, data):
            if not isinstance(data, self.this_types):
                trace.exception(StructureTypeError(self.this_types, type(data), "Data"))
                return ...
            containers:list[tuple[Con[K], Con[V]]] = []
            for key, value in environment.domain.type_stuff.iterate_data(data):
                with trace.enter_key(key, value):
                    key_structure = self.get_key_structure(key, value, trace, environment)
                    value_structure = self.get_value_structure(key, value, trace, environment)
                    key_container = self.containerize_item(key, key_structure, trace, environment)
                    value_container = self.containerize_item(value, value_structure, trace, environment)
                    if key_container is not ... and value_container is not ...:
                        containers.append((key_container, value_container))
            return icon_from_list(containers, data)
        return ...

    def containerize_item[A](self, item:A, structure:Structure[A, Con[A], Don[A], Don[A]|Diff[Don[A]], Any, Any]|None, trace:Trace, environment:PrinterEnvironment) -> Con[A]|EllipsisType:
        if structure is None:
            return SCon(item, environment.domain)
        else:
            return structure.containerize(item, trace, environment)

    def diffize(
        self,
        data: ICon[Con[K], Con[V], D],
        bundle: tuple[int, ...],
        trace: Trace,
        environment: ComparisonEnvironment,
    ) -> Mapping[tuple[int, ...], IDon[Diff[Don[K]], Diff[Don[V]], D, Con[K], Con[V]]] | EllipsisType:
        # this method was very annoying.
        with trace.enter(self, self.name, data):
            diffed_items:list[Mapping[tuple[int,...], tuple[Diff[Don[K]], Diff[Don[V]]]]] = []
            current_length:int = 0
            for undiffed_key, undiffed_value in data.items(): # weird names because of lambda expressions.
                with trace.enter_key(undiffed_key, undiffed_value):
                    current_length += 1
                    diffed_key = self.diffize_item(undiffed_key, bundle, lambda branch: self.get_key_structure_chain_end(undiffed_key, undiffed_value, trace, environment[branch]), trace, environment)
                    diffed_value = self.diffize_item(undiffed_value, bundle, lambda branch: self.get_value_structure_chain_end(undiffed_key, undiffed_value, trace, environment[branch]), trace, environment)
                    diffed_items.append(self.combine_key_value(diffed_key, diffed_value, bundle))
            if current_length == 0: # If `data` is an empty ICon, then the above for loop will do nothing, leading eventually to a Diff with no items (bad).
                return {bundle: idon_from_list([], {branch: data for branch in bundle})}
            else:
                return {local_bundle: idon_from_list(items, {branch: data for branch in local_bundle}) for local_bundle, items in self.combine_bundles(diffed_items, bundle).items()}
        return ...

    def diffize_item[A](
        self,
        item:Con[A],
        bundle:tuple[int,...],
        structure_function:Callable[[int], Structure[A, Con[A], Don[A], Don[A]|Diff[Don[A]], Any, Any]|None],
        trace:Trace,
        environment:ComparisonEnvironment,
    ) -> dict[tuple[int,...], Don[A]]:
        structures = [(branch, structure := structure_function(branch)) for branch in bundle]
        structure_bundles:list[tuple[tuple[int,...], Structure[A, Con[A], Don[A], Don[A]|Diff[Don[A]], Any, Any]|None]] = []
        current_bundle:list[int] = []
        current_structure:Structure[A, Con[A], Don[A], Don[A]|Diff[Don[A]], BO, CO]|None|EllipsisType = ...
        for branch, structure in structures:
            if current_structure is ... or structure is current_structure:
                current_bundle.append(branch)
            else:
                structure_bundles.append((tuple(current_bundle), current_structure))
                current_bundle = [branch]
            current_structure = structure
        assert current_structure is not ...
        structure_bundles.append((tuple(current_bundle), current_structure))
        output:dict[tuple[int,...], Don[A]] = {}
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

    def combine_key_value(self, key_diff:Mapping[tuple[int,...], Don[K]], value_diff:Mapping[tuple[int,...], Don[V]], top_bundle:tuple[int,...]) -> Mapping[tuple[int,...], tuple[Diff[Don[K]], Diff[Don[V]]]]:
        bundle_ends:set[int] = {bundle[-1] for item_diff in (key_diff, value_diff) for bundle in item_diff}
        output:dict[tuple[int,...], tuple[dict[tuple[int,...], Don[K]], dict[tuple[int,...], Don[V]]]] = {} # lists are one-item (if not one-item, broken; help)
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
        return {bundle: (Diff(key_list, False), Diff(value_list, False)) for bundle, (key_list, value_list) in output.items()}

    def type_check(self, data: ICon[Con[K], Con[V], D], trace: Trace, environment: PrinterEnvironment) -> None:
        with trace.enter(self, self.name, data):
            self.type_check_item(data.data, self.this_types, "Data", trace)
            required_keys:set[str] = self.required_keys.copy()
            for key, value in data.items():
                with trace.enter_key(key, value):
                    value_types = self.get_value_types(key.data, value.data, trace, environment)
                    self.type_check_item(key.data, self.key_types, "Key", trace)
                    self.type_check_item(value.data, value_types, "Value", trace)
                    key_structure = self.get_key_structure(key.data, value.data, trace, environment)
                    value_structure = self.get_value_structure(key.data, value.data, trace, environment)
                    if key_structure is not None:
                        key_structure.type_check(key, trace, environment)
                    if value_structure is not None:
                        value_structure.type_check(value, trace, environment)
                    if len(required_keys) > 0:
                        required_keys.discard(self.key_function(key.data))
            if len(required_keys) != 0:
                trace.exceptions(StructureRequiredKeyMissingError(self, key) for key in sorted(required_keys))

    def type_check_item(self, item:object, types:tuple[type,...], label:str, trace:Trace) -> None:
        if not isinstance(item, types):
            trace.exception(StructureTypeError(types, type(item), label))

    def get_tag_paths(self, data: ICon[Con[K], Con[V], D], tag:StructureTag, data_path: DataPath, trace: Trace, environment: PrinterEnvironment) -> Sequence[DataPath]:
        with trace.enter(self, self.name, data):
            if tag not in self.children_tags:
                return ()
            output:list[DataPath] = []
            if tag in self.tags:
                output.extend(data_path.copy(key.data).embed(value.data) for key, value in data.items())
            for key, value in data.items():
                with trace.enter_key(key, value), data_path.append(key.data):
                    key_structure = self.get_key_structure(key.data, value.data, trace, environment)
                    value_structure = self.get_value_structure(key.data, value.data, trace, environment)
                    if key_structure is not None:
                        output.extend(key_structure.get_tag_paths(key, tag, data_path, trace, environment))
                    if value_structure is not None:
                        output.extend(value_structure.get_tag_paths(value, tag, data_path, trace, environment))
            return output
        return () # error occurred

    def get_value_type_use(self, key:Con[K], value:Con[V], usage_tracker:UsageTracker, parent_use:Use|None, trace:Trace, environment:PrinterEnvironment) -> TypeUse:
        value_types = self.get_value_types(key.data, value.data, trace, environment)
        for value_type in value_types:
            if isinstance(value.data, value_type):
                return TypeUse(value_type, Region.value_types, NonEmptyUse(self, None, StructureUse(self, None, parent_use)), usage_tracker)
        else: raise StructureTypeError(value_types, type(key.data), "Value")

    def always_empty(self) -> bool: # gives empty KeymapStructure the ability to refuse a NonEmptyUse being unused.
        return False

    def get_key_value_parent_use(self, key:Con[K], value:Con[V], non_empty_use:NonEmptyUse) -> Use:
        return non_empty_use

    def get_uses(self, data: ICon[Con[K], Con[V], D], usage_tracker:UsageTracker, parent_use:Use|None, trace: Trace, environment: PrinterEnvironment) -> OrderedSet[Use]:
        if not usage_tracker.still_used(self): return OrderedSet(())
        with trace.enter(self, self.name, data):
            output:OrderedSet[Use] = OrderedSet(())
            self_use:StructureUse[IterableStructure] = StructureUse(self, usage_tracker, parent_use)
            non_empty_use = NonEmptyUse(self, usage_tracker, self_use, self.always_empty())
            output.add(self_use)
            current_length:int = 0
            for this_type in self.this_types:
                if isinstance(data.data, this_type):
                    output.add(TypeUse(this_type, Region.this_types, non_empty_use, usage_tracker))
                    break
            else: raise StructureTypeError(self.this_types, type(data.data), "Data")
            for key, value in data.items():
                current_length += 1
                with trace.enter_key(key, value):
                    for key_type in self.key_types:
                        if isinstance(key.data, key_type):
                            output.add(TypeUse(key_type, Region.key_types, non_empty_use, usage_tracker))
                            break
                    else: raise StructureTypeError(self.key_types, type(key.data), "Key")
                    output.add(self.get_value_type_use(key, value, usage_tracker, parent_use, trace, environment))
                    key_structure = self.get_key_structure(key.data, value.data, trace, environment)
                    if key_structure is not None:
                        output.update(key_structure.get_uses(key, usage_tracker, self.get_key_value_parent_use(key, value, non_empty_use) if key_structure.is_inline else None, trace, environment))
                    value_structure = self.get_value_structure(key.data, value.data, trace, environment)
                    if value_structure is not None:
                        output.update(value_structure.get_uses(value, usage_tracker, self.get_key_value_parent_use(key, value, non_empty_use) if value_structure.is_inline else None, trace, environment))
            if current_length > 0:
                output.add(non_empty_use)
            return output
        return OrderedSet(())

    def get_all_uses(self, memo:set[Structure], parent_use:Use|None, ) -> OrderedSet[Use]:
        if self in memo: return OrderedSet(())
        self_use:StructureUse[IterableStructure] = StructureUse(self, None, parent_use)
        non_empty_use = NonEmptyUse(self, None, self_use, self.always_empty())
        output:OrderedSet[Use] = OrderedSet((self_use, non_empty_use))
        for this_type in self.this_types:
            output.add(TypeUse(this_type, Region.this_types, non_empty_use, None))
        for key_type in self.key_types:
            output.add(TypeUse(key_type, Region.key_types, non_empty_use, None))
        memo.add(self)
        return output

    def print_branch(self, data: ICon[Con[K], Con[V], D], trace: Trace, environment: PrinterEnvironment) -> BO|EllipsisType:
        with trace.enter(self, self.name, data):
            if self.delegate is None:
                raise AttributeNoneError("delegate", self)
            return self.delegate.print_branch(data, trace, environment)
        return ...

    def print_comparison(self, data: IDon[Diff[Don[K]], Diff[Don[V]], D, Con[K], Con[V]], bundle:tuple[int,...], trace: Trace, environment: ComparisonEnvironment) -> CO|EllipsisType:
        with trace.enter(self, self.name, data):
            if self.delegate is None:
                raise AttributeNoneError("delegate", self)
            return self.delegate.print_comparison(data, bundle, trace, environment)
        return ...

    # the below methods are utility methods for use in multiple subclasses.

    def get_key_similarity(self, key1:Con[K], key2:Con[K], value1:Con[V], value2:Con[V], branch1:int, branch2:int, trace:Trace, environment:ComparisonEnvironment) -> tuple[float, bool]:
        if key1 == key2:
            return 1.0, True

        structure1 = self.get_key_structure(key1.data, value1.data, trace, (environment1 := environment[branch1]))
        if structure1 is None:
            return float(is_similar := (key1 == key2)), is_similar
        structure2 = self.get_key_structure(key2.data, value2.data, trace, (environment2 := environment[branch2]))
        if structure2 is None:
            return float(is_similar := (key1 == key2)), is_similar

        structure1_chain_end = structure1.get_structure_chain_end(key1, trace, environment1)
        if structure1_chain_end is None:
            return float(is_similar := (key1 == key2)), is_similar
        structure2_chain_end = structure2.get_structure_chain_end(key2, trace, environment2)
        if structure1_chain_end is not structure2_chain_end:
            return float(is_similar := (key1 == key2)), is_similar
        return structure1_chain_end.get_similarity(key1, key2, branch1, branch2, trace, environment)

    def get_value_similarity(self, key1:Con[K], key2:Con[K], value1:Con[V], value2:Con[V], branch1:int, branch2:int, trace:Trace, environment:ComparisonEnvironment) -> tuple[float, bool]:
        if value1 == value2:
            return 1.0, True

        structure1 = self.get_value_structure(key1.data, value1.data, trace, (environment1 := environment[branch1]))
        if structure1 is None:
            return float(is_similar := (value1 == value2)), is_similar
        structure2 = self.get_value_structure(key2.data, value2.data, trace, (environment2 := environment[branch2]))
        if structure2 is None:
            return float(is_similar := (value1 == value2)), is_similar

        structure1_chain_end = structure1.get_structure_chain_end(value1, trace, environment1)
        if structure1_chain_end is None:
            return float(is_similar := (value1 == value2)), is_similar
        structure2_chain_end = structure2.get_structure_chain_end(value2, trace, environment2)
        if structure1_chain_end is not structure2_chain_end:
            return float(is_similar := (value1 == value2)), is_similar
        return structure1_chain_end.get_similarity(value1, value2, branch1, branch2, trace, environment)

    def assemble_output(
        self,
        cumulative_items:list[tuple[list[tuple[list[int], Con[K]]], list[tuple[list[int], Con[V]]]]],
        trace:Trace,
        environment:ComparisonEnvironment,
    ) -> tuple[list[tuple[Diff[Don[K]], Diff[Don[V]]]], bool]:
        output:list[tuple[Diff[Don[K]], Diff[Don[V]]]] = []
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
        item_diff:list[tuple[list[int], Con[A]]],
        structure_function:Callable[[Con[A], int],Structure[A, Con[A], Don[A], Don[A]|Diff[Don[A]], Any, Any]|None],
        trace:Trace,
        environment:ComparisonEnvironment,
    ) -> tuple[Diff[Don[A]], bool]: # Diff and if the Diff has any internal changes.
        structure_bundles:list[tuple[Structure[A, Con[A], Don[A], Don[A]|Diff[Don[A]], Any, Any]|None, list[tuple[tuple[int,...], Con[A]]]]] = []
        for bundle, item in item_diff:
            previous_structure, previous_bundles = structure_bundles[-1] if len(structure_bundles) != 0 else (..., [])
            structure = structure_function(item, bundle[-1])
            if previous_structure is structure:
                # cannot occur if `previous_structure` is ...; therefore, the problem with `previous_bundles` not being inside anything DNE.
                previous_bundles.append((tuple(bundle), item))
            else:
                structure_bundles.append((structure, [(tuple(bundle), item)]))
        internal_changes:bool = False
        advanced_diff:dict[tuple[int,...], Don[A]] = {}
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
                elif isinstance(comparison_output, Diff):
                    advanced_diff.update(comparison_output.items)
                else:
                    # if comparison_output is an IDon, then any change becomes an internal change.
                    internal_changes = internal_changes or any_changes
                    advanced_diff[tuple(branch for bundle, _ in bundles for branch in bundle)] = comparison_output
        return Diff(advanced_diff, internal_changes), internal_changes
