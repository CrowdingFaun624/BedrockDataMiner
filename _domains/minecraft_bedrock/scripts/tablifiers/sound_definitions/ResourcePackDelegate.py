from types import EllipsisType
from typing import Any

from _domains.minecraft_bedrock.scripts.tablifiers.sound_definitions.make_all_tags import (
    make_all_tags,
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

    type_verifier = TypedDictTypeVerifier()

    applies_to = (IterableStructure,)

    def print_comparison(
        self,
        data: Diff[IDon[Diff[SDon[str]], Diff[IDon[Diff[Any], Diff[Any], dict[Any, Any], Any, Any]], dict[str,dict[Any, Any]], SCon[str], ICon[Any, Any, dict[Any,Any]]]],
        trace: Trace,
        environment: ComparisonEnvironment
    ) -> str | EllipsisType:
        output:list[str] = []
        # sorts data according to tag.
        assert data.length == 1
        data_dict = {
            ",".join(sorted(key[0, 1][1].split(","), key=lambda item: make_all_tags.TAG_ORDER[item])): (value[0, 1], list(value.last_value.items())) # value is not allowed to be a shallow change.
            for key, value in sorted(data.last_value.items(), key=lambda item: sorted(tuple(make_all_tags.TAG_ORDER[pack] for pack in item[0].last_value.last_value.split(","))))
        }
        for resource_pack_name, (resource_pack_data, resource_pack_data_list) in data_dict.items():
            with trace.enter_key(resource_pack_name, resource_pack_data):
                if len(resource_pack_data_list) == 0:
                    continue

                structure = self.structure.get_value_structure(resource_pack_name, resource_pack_data[1], trace, environment[1])
                assert structure is not None
                comparison = structure.print_comparison(resource_pack_data, trace, environment)
                if comparison is ...:
                    continue
                output.append(f"=== {" ".join(pack.capitalize() for pack in resource_pack_name.split(","))} ===\n")
                output.append(f"{{| class=\"wikitable sortable\" data-description=\"List of {resource_pack_name.replace(",", " ")} sound events\"\n")
                output.append("! Sound Event !! Sound Files Used !! Category\n|-\n")
                output.append(comparison)
                output.append("\n|}\n\n")
        return "".join(output)
