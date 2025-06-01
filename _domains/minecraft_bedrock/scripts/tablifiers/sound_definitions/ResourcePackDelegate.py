from types import EllipsisType
from typing import Any

import _domains.minecraft_bedrock.scripts.tablifiers.sound_definitions.make_all_tags as make_all_tags
import Structure.Delegate.Delegate as Delegate
import Structure.Difference as Diff
import Structure.IterableContainer as ICon
import Structure.IterableStructure as IterableStructure
import Structure.SimpleContainer as SCon
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

__all__ = ("ResourcePackDelegate",)


class ResourcePackDelegate(Delegate.Delegate[
    ICon.ICon[SCon.SCon[str], ICon.ICon[Any, Any, dict[Any, Any]], dict[str,dict[Any, Any]]],
    ICon.IDon[Diff.Diff[SCon.SDon[str]], Diff.Diff[ICon.IDon[Diff.Diff[Any], Diff.Diff[Any], dict[Any, Any], Any, Any]], dict[str,dict[Any, Any]], SCon.SCon[str], ICon.ICon[Any, Any, dict[Any,Any]]],
    IterableStructure.IterableStructure[str, dict[Any,Any], dict[str,dict[Any,Any]], Any, Any, Any, str, Any, str],
    str, Any, str, Any,
]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier()

    applies_to = (IterableStructure.IterableStructure,)

    def print_comparison(
        self,
        data: ICon.IDon[Diff.Diff[SCon.SDon[str]], Diff.Diff[ICon.IDon[Diff.Diff[Any], Diff.Diff[Any], dict[Any, Any], Any, Any]], dict[str,dict[Any, Any]], SCon.SCon[str], ICon.ICon[Any, Any, dict[Any,Any]]],
        trace: Trace.Trace,
        environment: StructureEnvironment.ComparisonEnvironment
    ) -> str | EllipsisType:
        output:list[str] = []
        # sorts data according to tag.
        data_dict = {
            ",".join(sorted(key[0, 1][1].split(","), key=lambda item: make_all_tags.TAG_ORDER[item])): (value[0, 1], list(value.last_value.items())) # value is not allowed to be a shallow change.
            for key, value in sorted(data.items(), key=lambda item: sorted(tuple(make_all_tags.TAG_ORDER[pack] for pack in item[0].last_value.last_value.split(","))))
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
