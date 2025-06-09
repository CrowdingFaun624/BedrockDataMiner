from types import EllipsisType
from typing import Any

from _domains.minecraft_bedrock.scripts.tablifiers.sound_definitions.make_all_tags import (
    TAG_ORDER,
)
from Structure.Delegate.Delegate import Delegate
from Structure.Difference import Diff
from Structure.IterableContainer import ICon, IDon
from Structure.IterableStructure import IterableStructure
from Structure.SimpleContainer import SCon, SDon
from Structure.StructureEnvironment import ComparisonEnvironment
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictTypeVerifier

__all__ = ("ResourcePackDelegate",)


class ResourcePackDelegate(Delegate[
    ICon[SCon[str], ICon[Any, Any, dict[Any, Any]], dict[str,dict[Any, Any]]],
    Diff[IDon[Diff[SDon[str]], Diff[IDon[Diff[Any], Diff[Any], dict[Any, Any], Any, Any]], dict[str,dict[Any, Any]], SCon[str], ICon[Any, Any, dict[Any,Any]]]],
    IterableStructure[str, dict[Any,Any], dict[str,dict[Any,Any]], Any, Any, Any, str, Any, str],
    str, Any, str, Any,
]):

    __slots__ = ()
    type_verifier = TypedDictTypeVerifier()

    applies_to = (IterableStructure,)

    def print_comparison(
        self,
        data: Diff[IDon[Diff[SDon[str]], Diff[IDon[Diff[Any], Diff[Any], dict[Any, Any], Any, Any]], dict[str,dict[Any, Any]], SCon[str], ICon[Any, Any, dict[Any,Any]]]],
        bundle:tuple[int,...],
        trace: Trace,
        environment: ComparisonEnvironment
    ) -> str | EllipsisType:
        output:list[str] = []
        # sorts data according to tag.
        assert data.length == 1
        data_dict = {
            ",".join(sorted(key.last_value.last_value.split(","), key=lambda item: TAG_ORDER[item])): (value.last_value, list(value.last_value.items()))
            for key, value in sorted(data.last_value.items(), key=lambda item: sorted(tuple(TAG_ORDER[pack] for pack in item[0].last_value.last_value.split(","))))
        }
        for resource_pack_name, (resource_pack_data, resource_pack_data_list) in data_dict.items():
            with trace.enter_key(resource_pack_name, resource_pack_data):
                if len(resource_pack_data_list) == 0:
                    continue

                last_branch, last_container = list(resource_pack_data._containers.items())[-1]
                structure = self.structure.get_value_structure(resource_pack_name, last_container.data, trace, environment[last_branch])
                assert structure is not None
                comparison = structure.print_comparison(resource_pack_data, bundle, trace, environment)
                if comparison is ...:
                    continue
                output.append(f"=== {" ".join(pack.capitalize() for pack in resource_pack_name.split(","))} ===\n")
                output.append(f"{{|class=\"wikitable sortable\"data-description=\"List of {resource_pack_name.replace(",", " ")} sound events\"\n")
                output.append("!Sound Event!!Sound Files Used!!Category\n|-\n")
                output.append(comparison)
                output.append("\n|}\n\n")
        return "".join(output)
