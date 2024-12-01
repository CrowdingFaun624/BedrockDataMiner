from typing import Any

import _assets.scripts.tablifiers.sound_definitions.make_all_tags as make_all_tags
import Structure.Delegate.Delegate as Delegate
import Structure.DictStructure as DictStructure
import Structure.Difference as D
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["ResourcePackDelegate"]


class ResourcePackDelegate(Delegate.Delegate[str, DictStructure.DictStructure, str]):

    type_verifier = TypeVerifier.TypedDictTypeVerifier()

    applies_to = (DictStructure.DictStructure,)

    def compare_text(self, data:dict[str,dict[Any,Any]], environment: StructureEnvironment.ComparisonEnvironment) -> tuple[str, bool, list[Trace.ErrorTrace]]:
        output:list[str] = []
        exceptions:list[Trace.ErrorTrace] = []
        has_changes = False
        # sorts data according to tag.
        data = {
            ",".join(sorted(key.split(","), key=lambda item: make_all_tags.TAG_ORDER[item])): value
            for key, value in sorted(data.items(), key=lambda item: sorted(tuple(make_all_tags.TAG_ORDER[pack] for pack in item[0].split(","))))
        }
        for resource_pack_name, resource_pack_data in data.items():
            assert not isinstance(resource_pack_name, D.Diff)
            assert not isinstance(resource_pack_data, D.Diff)
            if len(resource_pack_data) == 0: continue

            structure, new_exceptions = self.get_structure().get_structure(resource_pack_name, resource_pack_data)
            exceptions.extend(exception.add(self.get_structure().name, resource_pack_name) for exception in new_exceptions)
            assert structure is not None
            comparison, any_changes, new_exceptions = structure.compare_text(D.last_value(resource_pack_data), environment)
            has_changes = has_changes or any_changes
            output.append("=== %s ===\n" % (" ".join(pack.capitalize() for pack in resource_pack_name.split(","))))
            output.append("{| class=\"wikitable sortable\" data-description=\"List of %s sound events\"\n" % (resource_pack_name.replace(",", " "),))
            output.append("! Sound Event !! Sound Files Used !! Category\n|-\n")
            output.append(comparison)
            output.append("\n|}\n\n")
        return "".join(output), has_changes, exceptions
