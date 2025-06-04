from functools import cache
from types import EllipsisType
from typing import Any, Callable, Hashable, NotRequired, TypedDict, cast

import Component.ComponentFunctions as ComponentFunctions
import Domain.Domain as Domain
from Structure.Container import Con, Don
from Structure.Delegate.LineDelegate import LineDelegate, LineType
from Structure.Difference import Diff
from Structure.IterableContainer import ICon, IDon
from Structure.IterableStructure import IterableStructure
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Structure.StructureTypes.KeymapStructure import KeymapStructure
from Utilities.Exceptions import StructureCannotPrintFlatError
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class DefaultDelegateKeysTypedDict(TypedDict):
    always_print: NotRequired[bool]

class DefaultDelegate[K:Hashable, V, D](LineDelegate[
    ICon[Con[K], Con[V], D],
    IDon[Diff[Don[K]], Diff[Don[V]], D, Con[K], Con[V]],
    IterableStructure[K, V, D, list[LineType], list[LineType], list[LineType], list[LineType], list[LineType], list[LineType]],
]):

    # NOTE: This class assumes that all diffs are of length 2

    applies_to = (IterableStructure,)

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("field", False, str),
        TypedDictKeyTypeVerifier("measure_length", False, bool),
        TypedDictKeyTypeVerifier("passthrough", False, bool),
        TypedDictKeyTypeVerifier("print_all", False, bool),
        TypedDictKeyTypeVerifier("print_flat", False, bool),
        TypedDictKeyTypeVerifier("show_item_key", False, bool),
        TypedDictKeyTypeVerifier("enquote_strings", False, bool),
        TypedDictKeyTypeVerifier("sort", False, (str, type(None))),
    )

    key_type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("always_print", False, bool),
    )

    __slots__ = (
        "always_print_keys",
        "key_function",
        "keys_order",
        "measure_length",
        "print_all",
        "print_flat",
        "show_item_key",
        "sorting_function",
        "sorting_function_name",
    )

    def __init__(
        self,
        structure:IterableStructure,
        keys:dict[str,DefaultDelegateKeysTypedDict],
        field:str="field",
        measure_length:bool=False,
        passthrough:bool=False,
        print_all:bool=False,
        print_flat:bool=False,
        show_item_key:bool=True,
        enquote_strings:bool=True,
        sort:str|None=None,
    ) -> None:
        super().__init__(structure, keys, field, enquote_strings, passthrough)
        self.measure_length = measure_length
        self.print_all = print_all
        self.print_flat = print_flat
        self.show_item_key = show_item_key
        self.sorting_function_name = sort
        self.always_print_keys = {key for key, value in keys.items() if value.get("always_print", False)}
        self.keys_order = {key: index for index, key in enumerate(keys.keys())}

    def finalize(self, domain:"Domain.Domain", trace:Trace) -> None:
        self.key_function = self.structure.key_function if isinstance(self.structure, KeymapStructure) else None
        if self.sorting_function_name is None:
            self.sorting_function = None
        else:
            sorting_function_function:ComponentFunctions.sort_function = domain.callables.get(self.sorting_function_name, domain)
            key_function = cast(Any, self.key_function if self.key_function is not None else lambda a: a)
            self.sorting_function:ComponentFunctions.sort_inner_function|None = sorting_function_function(key_function, self.keys_order)

    def get_item_key(self, index:K) -> str:
        return " " + self.stringify(index) if self.show_item_key else ""

    def get_compare_text_key_str(self, index:K) -> K|None:
        return index if self.show_item_key else None

    def print_branch(self, data:ICon[Con[K], Con[V], D], trace:Trace, environment:PrinterEnvironment) -> list[LineType]|EllipsisType:
        output:list[LineType] = []
        items_str:list[str] = [] # print_flat only
        data_list = list(data.items())
        if self.sorting_function is not None:
            data_list.sort(key=self.sorting_function)
        for key, value in data_list:
            with trace.enter_key(key, value):
                key_output = self.get_item_output(key, self.structure.get_key_structure(key.data, value.data, trace, environment), trace, environment) if self.show_item_key else None
                value_output = self.get_item_output(value, self.structure.get_value_structure(key.data, value.data, trace, environment), trace, environment)
                if self.print_flat and len(value_output) == 1:
                    items_str.append(value_output[0][1])
                elif self.print_flat and len(value_output) != 1:
                    trace.exception(StructureCannotPrintFlatError())
                else:
                    self.print_single(key_output, value_output, output, add_punctuation=False)
        if self.print_flat:
            return [(0, "[" + ", ".join(items_str) + "]")]
        return output

    def print_comparison(self, data:IDon[Diff[Don[K]], Diff[Don[V]], D, Con[K], Con[V]], trace:Trace, environment:ComparisonEnvironment) -> list[LineType]|EllipsisType:
        output:list[LineType] = []
        current_length, addition_length, removal_length = 0, 0, 0
        size_changed = False
        data_list = list(data.items())
        if self.sorting_function is not None:
            data_list.sort(key=self.sorting_function)
        for key_diff, value_diff in data_list:
            with trace.enter_key(key_diff, value_diff):
                can_print_print_all = True # if the print_all thing is overridden for whatever reason.
                key_output_representation:Callable[[],list[LineType]|None]

                # each of the below if statements must set both `key_output_representation` and `key_representation`.
                if not self.show_item_key:
                    key_representation = None
                    key_output_representation = lambda: None

                elif key_diff.contains_diffs: # because two total branches are assumed, if this is True, `key_diff` has only one bundle with both branches.
                    # value[1] (below) must exist because key[1] must exist.
                    key_structure = self.structure.get_key_structure(key_diff[1][1], value_diff[1][1], trace, environment[1])
                    # key_structure cannot be None because if it were None, `key_diff.contains_diff` must be False.
                    if key_structure is None:
                        continue
                    key_output = key_structure.print_comparison(key_diff[1], trace, environment)
                    if key_output is ...:
                        continue
                    self.print_single(None, key_output, output, message="Moved ")
                    key_representation = key_diff[1].get_con(1)
                    if key_representation is ...:
                        continue
                    good_key_structure = key_structure # used just for the lambda expression below.
                    good_key_representation = key_representation
                    key_output_representation = cache(lambda: key_output_representation_output if (key_output_representation_output := good_key_structure.print_branch(good_key_representation, trace, environment[1])) is not ... else [])

                elif key_diff.length > 1: # if there is a shallow change and both branches 0 and 1 exist.
                    key_representation = key_diff[1].get_con(1)
                    key_structure1 = self.structure.get_key_structure(key_diff[0][0], value_diff[0][0], trace, environment[0])
                    key_structure2 = self.structure.get_key_structure(key_representation.data, value_diff[1][1], trace, environment[1])
                    # key structures may be None.
                    key_output1 = self.get_item_output(key_diff[0].get_con(0), key_structure1, trace, environment[0])
                    key_output2 = self.get_item_output(key_representation, key_structure2, trace, environment[1])
                    self.print_double(None, key_output1, key_output2, "Moved ", output)
                    key_output_representation = lambda: key_output2
                # The two above cases cover all situations where the key moves.

                # The below case does not add to `output`, but they do create `key_output_representation`.
                else: # if the key is an addition or removal or unchanged.
                    branch = 1 if key_diff.value_exists_at(1) else 0
                    key_representation = key_diff[branch].get_con(branch)
                    key_structure = self.structure.get_key_structure(key_representation.data, value_diff[branch][branch], trace, environment[branch])
                    key_representation2 = key_representation # messing with variables to make lambdas happy.
                    key_output_representation = cache(lambda: self.get_item_output(key_representation2, key_structure, trace, environment[branch]))

                if value_diff.contains_diffs: # because two total branches are assumed, if this is True, `value_diff` has only one bundle with both branches.
                    current_length += 1
                    # key[1] (below) must exist because value[1] must exist.
                    value_structure = self.structure.get_value_structure(key_diff[1][1], value_diff[1][1], trace, environment[1])
                    # value_structure cannot be None because if it were None, `value_diff.contains_diff` must be False.
                    if value_structure is None:
                        continue
                    value_output = value_structure.print_comparison(value_diff[1], trace, environment)
                    if value_output is ...:
                        continue
                    self.print_single(key_output_representation(), value_output, output, message="Changed ", allow_single_line=False)

                elif value_diff.length > 1: # if there is a shallow change and both branches 0 and 1 exist.
                    current_length += 1
                    value_structure1 = self.structure.get_value_structure(key_diff[0][0], value_diff[0][0], trace, environment[0])
                    value_structure2 = self.structure.get_value_structure(key_diff[1][1], value_diff[1][1], trace, environment[1])
                    # value structures may be None
                    value_output1 = self.get_item_output(value_diff[0].get_con(0), value_structure1, trace, environment[0])
                    value_output2 = self.get_item_output(value_diff[1].get_con(1), value_structure2, trace, environment[1])
                    self.print_double(key_output_representation(), value_output1, value_output2, "Changed ", output)

                elif not value_diff.value_exists_at(0) or not value_diff.value_exists_at(1):
                    size_changed = True
                    branch = 1 if value_diff.value_exists_at(1) else 0
                    if branch == 1:
                        current_length += 1; addition_length += 1
                    else:
                        removal_length += 1
                    value_structure = self.structure.get_value_structure(key_diff[branch][branch], value_diff[branch][branch], trace, environment[branch])
                    message = "Added " if branch == 1 else "Removed "
                    value_output = self.get_item_output(value_diff[branch].get_con(branch), value_structure, trace, environment[branch])
                    self.print_single(key_output_representation(), value_output, output, message=message)

                elif can_print_print_all and (self.print_all or (self.key_function is not None and key_representation is not None and self.key_function(key_representation.data) in self.always_print_keys)):
                    # no change occured and it needs to be documented.
                    current_length += 1
                    value_structure = self.structure.get_value_structure(key_diff[1][1], value_diff[1][1], trace, environment[1])
                    value_output = self.get_item_output(value_diff[1].get_con(1), value_structure, trace, environment[1])
                    self.print_single(key_output_representation(), value_output, output, message="Unchanged ")

                else:
                    # no change occurred and it does not need to be documented.
                    current_length += 1

        if self.measure_length and size_changed:
            output = [(0, f"Total {self.field}: {current_length} (+{addition_length}, -{removal_length})")] + output
        return output
