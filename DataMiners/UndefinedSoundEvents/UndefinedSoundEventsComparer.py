from typing import TYPE_CHECKING

import Comparison.Comparer as Comparer
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.UndefinedSoundEvents, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.UndefinedSoundEvents:
    resource_packs:DataMinerTyping.ResourcePacks = dataminers["resource_packs"].get_data_file(version, non_exist_ok=True)
    if resource_packs is None:
        resource_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}]
    for sound_event_name, traces in data.items():
        pass

comparer = Comparer.Comparer(
    normalizer=None,
    dependencies=["resource_packs"],
    base_comparer_section=Comparer.DictComparerSection(
        name="sound event",
        key_types=(str,),
        value_types=(list,),
        detect_key_moves=True,
        measure_length=True,
        comparer=Comparer.ListComparerSection(
            name="trace",
            types=(list,),
            ordered=False,
            measure_length=True,
            comparer=Comparer.ListComparerSection(
                name="item",
                types=(str,),
                ordered=True,
                print_flat=True,
                comparer=None
            )
        )
    )
)
