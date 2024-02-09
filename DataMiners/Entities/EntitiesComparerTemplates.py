from typing import Callable

import Comparison.Comparer as Comparer

decimal = float|int

def get_filter_comparer() -> Comparer.DictComparerSection:
    types = [
        ["all_of", list, None],
        ["any_of", list, None],
        ("domain", str, None),
        ["none_of", list, None],
        ("operator", str, None),
        ("other_with_families", str, None),
        ("subject", str, None),
        ("test", str, None),
        ("value", (bool, decimal, str), None),
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

filter_list_comparer = Comparer.ListComparerSection(
    name="filter",
    types=(dict,),
    measure_length=True,
    ordered=False,
    comparer=filter_comparer
)

filter_maybe_list_comparer = [
    (lambda key, value: isinstance(value, dict), filter_comparer),
    (lambda key, value: isinstance(value, list), filter_list_comparer),
]

many_filters_comparer = Comparer.DictComparerSection(
    name="filters",
    key_types=(str,),
    value_types=(list,),
    measure_length=True,
    comparer=filter_list_comparer
)

range_comparer = Comparer.ListComparerSection(
    name="range",
    types=(decimal,),
    print_flat=True,
    ordered=True,
    comparer=None
)

range_dict_comparer = Comparer.UnnamedDictComparerSection(
    ("range_min", decimal, None),
    ("range_max", decimal, None),
)

coordinate_comparer = Comparer.ListComparerSection(
    name="coordinate",
    types=(decimal,),
    print_flat=True,
    comparer=None,
)

damage_comparer=[
    ("catch_fire", bool, None),
    ("damage", (dict, decimal, list), [
        (lambda key, value: isinstance(value, dict), range_dict_comparer),
        (lambda key, value: isinstance(value, decimal), None),
        (lambda key, value: isinstance(value, list), range_comparer),
    ]),
    ("destroy_on_hit", bool, None),
    ("effect_name", str, None),
    ("effect_duration", int, None),
    ("filter", str, None),
    ("knockback", bool, None),
    ("max_critical_damage", int, None),
    ("min_critical_damage", int, None),
    ("power_multiplier", decimal, None),
    ("semi_random_diff_damage", bool, None),
    ("should_bounce", bool, None),
]

value_comparer = Comparer.UnnamedDictComparerSection(
    ("value", (bool, decimal), None),
)

value_max_comparer = Comparer.UnnamedDictComparerSection(
    ("value", (bool, decimal), None),
    ("max", (bool, decimal), None),
)

event_target_comparer = Comparer.UnnamedDictComparerSection(
    ("event", str, None),
    ("target", str, None),
)

event_target_list_comparer = Comparer.ListComparerSection(
    name="event",
    ordered=False,
    measure_length=True,
    types=(dict,),
    comparer=event_target_comparer
)

event_target_filters_comparer = Comparer.UnnamedDictComparerSection(
    ("event", str, None),
    ("filters", (dict, list), filter_maybe_list_comparer),
    ("target", str, None),
)

event_target_filters_list_comparer = Comparer.ListComparerSection(
    name="event",
    ordered=False,
    measure_length=True,
    types=(dict,),
    comparer=event_target_filters_comparer
)

conditional_bandwidth_optimization_values_comparer = Comparer.UnnamedDictComparerSection(
    ("conditional_values", list, filter_list_comparer),
    ("max_dropped_ticks", int, None),
    ("max_optimized_distance", decimal, None),
    ("use_motion_prediction_hints", bool, None),
)

item_list_comparer = Comparer.ListComparerSection(
    name="item",
    types=(str,),
    ordered=False,
    measure_length=True,
    comparer=None,
)

block_list_comparer = Comparer.ListComparerSection(
    name="block",
    ordered=False,
    measure_length=True,
    types=(str,),
    comparer=None
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
    ("filters", (dict, list), filter_maybe_list_comparer),
    ("max_wait_time", int, None),
    ("min_wait_time", int, None),
    ("num_to_spawn", int, None),
    ("should_leash", bool, None),
    ("single_use", bool, None),
    ("spawn_entity", str, None),
    ("spawn_event", str, None),
    ("spawn_item", str, None),
    ("spawn_item_event", dict, event_target_comparer),
    ("spawn_method", str, None),
    ("spawn_sound", str, None),
)

interaction_comparer = Comparer.UnnamedDictComparerSection(
    ("add_items", dict, Comparer.UnnamedDictComparerSection(
        ("table", str, None),
    )),
    ("admire", bool, None),
    ("barter", bool, None),
    ("cooldown", decimal, None),
    ("cooldown_after_being_attacked", decimal, None),
    ("drop_item_slot", int, None),
    ("equip_item_slot", int, None),
    ("give_item", bool, None),
    ("health_amount", int, None),
    ("hurt_item", int, None),
    ("interact_text", str, None),
    ("on_interact", dict, event_target_filters_comparer),
    ("particle_on_start", dict, Comparer.UnnamedDictComparerSection(
        ("particle_type", str, None),
        ("particle_y_offset", decimal, None),
        ("particle_offset_towards_interactor", bool, None),
    )),
    ("play_sounds", str, None),
    ("spawn_items", dict, Comparer.UnnamedDictComparerSection(
        ("table", str, None),
    )),
    ("swing", bool, None),
    ("take_item", bool, None),
    ("transform_to_item", str, None),
    ("use_item", bool, None),
    ("vibration", str, None),
    name="interaction"
)

entity_types_comparer = Comparer.UnnamedDictComparerSection(
    ("check_if_outnumbered", bool, None),
    ("cooldown", int, None),
    ("filters", dict, filter_comparer),
    ("max_dist", decimal, None),
    ("max_flee", int, None),
    ("must_see", bool, None),
    ("priority", int, None),
    ("reevaluate_description", bool, None),
    ("sprint_speed_multiplier", decimal, None),
    ("walk_speed_multiplier", decimal, None),
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
        ("cast_duration", decimal, None),
        ("cooldown_time", decimal, None),
        ("filters", dict, filter_comparer),
        ("max_activation_range", decimal, None),
        ("min_activation_range", decimal, None),
        ("particle_color", str, None),
        ("sequence", list, Comparer.ListComparerSection(
            name="sequence item",
            types=(dict,),
            ordered=True,
            measure_length=True,
            comparer=Comparer.UnnamedDictComparerSection(
                ("base_delay", decimal, None),
                ("delay_per_summon", decimal, None),
                ("entity_lifespan", decimal, None),
                ("entity_type", str, None),
                ("event", str, None),
                ("num_entities_spawned", int, None),
                ("shape", str, None),
                ("size", decimal, None),
                ("sound_event", str, None),
                ("summon_cap", int, None),
                ("summon_cap_radius", decimal, None),
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
        ("emit_vibration", dict, Comparer.UnnamedDictComparerSection(
            ("vibration", str, None),
        )),
        ("filters", dict, filter_comparer),
        ["randomize", list, None],
        ("remove", dict, events_add_remove_comparer),
        ["sequence", list, None],
        ("set_property", dict, Comparer.DictComparerSection(
            name="property",
            key_types=(str,),
            value_types=(bool, str),
            measure_length=True,
            comparer=None
        )),
        ("trigger", str, None),
        ("weight", int, None),
    ]
    types[3][2] = Comparer.ListComparerSection(
        name="randomize item",
        ordered=False,
        types=(dict,),
        measure_length=True,
        comparer=Comparer.UnnamedDictComparerSection(
            *types
        )
    )
    
    types[5][2] = Comparer.ListComparerSection(
        name="sequence item",
        ordered=True,
        types=(dict,),
        measure_length=True,
        comparer=Comparer.UnnamedDictComparerSection(
            *types
        )
    )
    types[3] = tuple(types[3])
    types[5] = tuple(types[5])
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
    ("damage_modifier", decimal, None),
    ("damage_multiplier", decimal, None),
    ("deals_damage", bool, None),
    ("on_damage", dict, event_target_filters_comparer),
    ("on_damage_sound_event", str, None),
)

entity_sensor_types = [
    ("event", str, None),
    ("event_filters", dict, filter_comparer),
    ("minimum_count", int, None),
    ("relative_range", bool, None),
    ("require_all", bool, None),
    ("sensor_range", decimal, None),
    ["subsensors", list, None]
]

entity_sensor_comparer =\
("minecraft:entity_sensor", dict, Comparer.UnnamedDictComparerSection(
    *entity_sensor_types
))

entity_sensor_types[6][2] = Comparer.ListComparerSection(
    name="subsensor",
    ordered=False,
    measure_length=True,
    types=(dict,),
    comparer=entity_sensor_comparer
)
entity_sensor_types[6] = tuple(entity_sensor_types[6])

shooter_types = [
    ("aux_val", int, None),
    ("def", str, None),
    ("magic", bool, None),
    ("power", decimal, None),
    ["projectiles", list, None],
    ("sound", str, None),
    ("type", str, None),
]

shooter_comparer = Comparer.UnnamedDictComparerSection(
    *shooter_types
)

shooter_types[4][2] = Comparer.ListComparerSection(
    name="projectile",
    measure_length=True,
    ordered=False,
    types=(dict,),
    comparer=shooter_comparer
)
shooter_types[4] = tuple(shooter_types[4])
