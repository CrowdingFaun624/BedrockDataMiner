from typing import Callable

import Comparison.Comparer as Comparer

def get_filter_comparer() -> Comparer.DictComparerSection:
    types = [
        ["all_of", list, None],
        ["any_of", list, None],
        ("domain", str, None),
        ["none_of", list, None],
        ("operator", str, None),
        ("subject", str, None),
        ("test", str, None),
        ("value", (bool, float, int, str), None),
    ]
    typed_dict = Comparer.TypedDictComparerSection(
        name="filter property",
        types=types
    )
    list_comparer_section = Comparer.ListComparerSection(
        name="filter",
        types=(dict,),
        measure_length=True,
        ordered=False,
        comparer=typed_dict
    )
    types[0][2] = list_comparer_section
    types[1][2] = list_comparer_section
    types[3][2] = list_comparer_section
    types[0] = tuple(types[0])
    types[1] = tuple(types[1])
    types[3] = tuple(types[3])
    return typed_dict


filter_comparer = get_filter_comparer()

many_filters_comparer = Comparer.DictComparerSection(
    name="filters",
    key_types=(str,),
    value_types=(list,),
    measure_length=True,
    comparer=Comparer.ListComparerSection(
        name="filter",
        types=(dict,),
        measure_length=True,
        ordered=False,
        comparer=filter_comparer
    )
)

range_comparer = Comparer.ListComparerSection(
    name="range",
    types=(float, int),
    print_flat=True,
    ordered=True,
    comparer=None
)

range_dict_comparer = Comparer.UnnamedDictComparerSection(
    ("range_min", (float, int), None),
    ("range_max", (float, int), None),
)

coordinate_comparer = Comparer.ListComparerSection(
    name="coordinate",
    types=(float, int),
    print_flat=True,
    comparer=None,
)

damage_comparer=[
    ("damage", (dict, int, list), [
        (lambda key, value: isinstance(value, dict), range_dict_comparer),
        (lambda key, value: isinstance(value, int), None),
        (lambda key, value: isinstance(value, list), range_comparer),
    ]),
    ("destroy_on_hit", bool, None),
    ("effect_name", str, None),
    ("effect_duration", int, None),
    ("knockback", bool, None),
    ("max_critical_damage", int, None),
    ("min_critical_damage", int, None),
    ("power_multiplier", float, None),
    ("semi_random_diff_damage", bool, None),
]

value_comparer = Comparer.UnnamedDictComparerSection(
    ("value", (bool, float, int), None),
)

value_max_comparer = Comparer.UnnamedDictComparerSection(
    ("value", (bool, float, int), None),
    ("max", (bool, float, int), None),
)

event_target_comparer = Comparer.UnnamedDictComparerSection(
    ("event", str, None),
    ("target", str, None),
)

event_target_filters_comparer = Comparer.UnnamedDictComparerSection(
    ("event", str, None),
    ("filters", (dict, list), [
        (lambda key, value: isinstance(value, dict), filter_comparer),
        (lambda key, value: isinstance(value, list), Comparer.ListComparerSection(
            name="filter",
            measure_length=True,
            ordered=False,
            types=(dict,),
            comparer=filter_comparer
        )),
    ]),
    ("target", str, None),
)

conditional_bandwidth_optimization_values_comparer = Comparer.UnnamedDictComparerSection(
    ("conditional_values", list, Comparer.ListComparerSection(
        name="filter",
        types=(dict,),
        ordered=False,
        measure_length=True,
        comparer=filter_comparer
    )),
    ("max_dropped_ticks", int, None),
    ("max_optimized_distance", float, None),
    ("use_motion_prediction_hints", bool, None),
)

item_list_comparer = Comparer.ListComparerSection(
    name="item",
    types=(str,),
    ordered=False,
    measure_length=True,
    comparer=None,
)

family_list_comparer = Comparer.ListComparerSection(
    name="family",
    types=(str,),
    comparer=None,
    ordered=True,
    measure_length=True,
)

seat_comparer = Comparer.UnnamedDictComparerSection(
    ("lock_rider_rotation", int, None),
    ("max_rider_count", int, None),
    ("min_rider_count", int, None),
    ("position", list, coordinate_comparer),
    ("rotate_rider_by", (int, str), None),
)

empty_dict_comparer = Comparer.UnnamedDictComparerSection()

spawn_entity_comparer = Comparer.UnnamedDictComparerSection(
    ("filters", dict, filter_comparer),
    ("max_wait_time", int, None),
    ("min_wait_time", int, None),
    ("spawn_item", str, None),
    ("spawn_sound", str, None),
)

interaction_comparer = Comparer.UnnamedDictComparerSection(
    ("add_items", dict, Comparer.UnnamedDictComparerSection(
        ("table", str, None),
    )),
    ("equip_item_slot", int, None),
    ("health_amount", int, None),
    ("hurt_item", int, None),
    ("interact_text", str, None),
    ("on_interact", dict, event_target_filters_comparer),
    ("play_sounds", str, None),
    ("swing", bool, None),
    ("transform_to_item", str, None),
    ("use_item", bool, None),
    name="interaction"
)

entity_types_comparer = Comparer.UnnamedDictComparerSection(
    ("filters", dict, filter_comparer),
    ("max_dist", (float, int), None),
    ("must_see", bool, None),
    ("priority", int, None),
    ("sprint_speed_multiplier", (float, int), None),
    ("walk_speed_multiplier", (float, int), None),
    ("within_default", int, None),
)

baby_comparer = Comparer.UnnamedDictComparerSection(
    ("mate_type", str, None),
    ("baby_type", str, None),
    ("breed_event", dict, event_target_comparer),
)

choice_comparer = Comparer.ListComparerSection(
    name="choice",
    ordered=False,
    measure_length=True,
    types=(dict,),
    comparer=Comparer.UnnamedDictComparerSection(
        ("cast_duration", float, None),
        ("cooldown_time", float, None),
        ("filters", dict, filter_comparer),
        ("max_activation_range", float, None),
        ("min_activation_range", float, None),
        ("particle_color", str, None),
        ("sequence", list, Comparer.ListComparerSection(
            name="sequence item",
            types=(dict,),
            ordered=True,
            measure_length=True,
            comparer=Comparer.UnnamedDictComparerSection(
                ("base_delay", float, None),
                ("delay_per_summon", float, None),
                ("entity_lifespan", float, None),
                ("entity_type", str, None),
                ("event", str, None),
                ("num_entities_spawned", int, None),
                ("shape", str, None),
                ("size", (float, int), None),
                ("sound_event", str, None),
                ("summon_cap", int, None),
                ("summon_cap_radius", float, None),
                ("target", str, None),
            )
        )),
        ("start_sound_event", str, None),
        ("weight", int, None),
    )
)

entity_types_comparers = [
    (lambda key, value: isinstance(value, dict), entity_types_comparer),
    (lambda key, value: isinstance(value, list), Comparer.ListComparerSection(
        name="entity type",
        types=(dict,),
        ordered=False,
        measure_length=True,
        comparer=entity_types_comparer
    )),
]

# TODO: phase this out entirely.
def get_component_key(name:str, sub_components:list[str]|None=None) -> Callable[[str],bool]:
    if not name.startswith("minecraft:"):
        raise ValueError("Component key \"%s\" does not start with \"minecraft:\"!" % name)
    if sub_components is None or len(sub_components) == 0:
        return name
    else:
        return [name] + [name + "." + sub_component for sub_component in sub_components]

events_add_remove_comparer = Comparer.UnnamedDictComparerSection(
    ("component_groups", list, Comparer.ListComparerSection(
        name="component group",
        types=(str,),
        ordered=False,
        measure_length=True,
        comparer=None,
    )),
)

def get_events_event_comparer() -> Comparer.DictComparerSection:
    # it's nested so it is evil.
    types = [
        ("add", dict, events_add_remove_comparer),
        ("filters", dict, filter_comparer),
        ["randomize", list, None],
        ("remove", dict, events_add_remove_comparer),
        ["sequence", list, None],
        ("trigger", str, None),
        ("weight", int, None),
    ]
    types[2][2] = Comparer.ListComparerSection(
        name="randomize item",
        ordered=False,
        types=(dict,),
        measure_length=True,
        comparer=Comparer.UnnamedDictComparerSection(
            *types
        )
    )
    
    types[4][2] = Comparer.ListComparerSection(
        name="sequence item",
        ordered=True,
        types=(dict,),
        measure_length=True,
        comparer=Comparer.UnnamedDictComparerSection(
            *types
        )
    )
    types[2] = tuple(types[2])
    types[4] = tuple(types[4])
    return Comparer.UnnamedDictComparerSection(
        *types
    )

events_comparer = Comparer.DictComparerSection(
    name="event",
    key_types=(str,),
    value_types=(dict,),
    measure_length=True,
    comparer=get_events_event_comparer()
)

damage_sensor_triggers_comparer = Comparer.UnnamedDictComparerSection(
    ("cause", str, None),
    ("deals_damage", bool, None),
    ("on_damage", dict, event_target_filters_comparer),
)
