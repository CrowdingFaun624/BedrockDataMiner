import Comparison.Comparer as Comparer

import DataMiners.Entities.EntitiesComparerBehaviors as EntitiesComparerBehaviors
import DataMiners.Entities.EntitiesComparerTemplates as EntitiesComparerTemplates

addrider_comparer =\
("minecraft:addrider", dict, Comparer.UnnamedDictComparerSection(
    ("entity_type", str, None),
))

ageable_comparer =\
("minecraft:ageable", dict, Comparer.UnnamedDictComparerSection(
    ("duration", int, None),
    ("feed_items", (list, str), [
        (lambda key, value: isinstance(value, list) and (len(value) == 0 or isinstance(value[0], str)), EntitiesComparerTemplates.item_list_comparer),
        (lambda key, value: isinstance(value, list) and isinstance(value[0], dict), Comparer.ListComparerSection(
            name="item",
            types=(dict,),
            ordered=False,
            measure_length=True,
            comparer=Comparer.UnnamedDictComparerSection(
                ("growth", float, None),
                ("item", str, None),
            )
        )),
        (lambda key, value: isinstance(value, str), None),
    ]),
    ("grow_up", dict, EntitiesComparerTemplates.event_target_comparer),
))

ambient_sound_interval_comparer =\
("minecraft:ambient_sound_interval", dict, Comparer.UnnamedDictComparerSection(
    ("value", (float, int), None),
    ("range", (float, int), None),
    ("event_name", str, None),
))

angry_comparer =\
("minecraft:angry", dict, Comparer.UnnamedDictComparerSection(
    ("broadcast_anger", bool, None),
    ("broadcast_range", int, None),
    ("duration", int, None),
    ("duration_delta", int, None),
    ("calm_event", dict, EntitiesComparerTemplates.event_target_comparer),
))

annotation_break_door_comparer =\
("minecraft:annotation.break_door", dict, EntitiesComparerTemplates.empty_dict_comparer)

attack_comparer =\
("minecraft:attack", dict, Comparer.UnnamedDictComparerSection(
    *EntitiesComparerTemplates.damage_comparer
))

attack_damage_comparer =\
("minecraft:attack_damage", dict, EntitiesComparerTemplates.value_comparer)

balloon_comparer =\
("minecraft:balloon", dict, Comparer.UnnamedDictComparerSection(
    ("lift_force", list, EntitiesComparerTemplates.coordinate_comparer),
))

balloonable_comparer =\
("minecraft:balloonable", dict, Comparer.UnnamedDictComparerSection(
    ("mass", float, None),
))

block_climber_comparer =\
("minecraft:block_climber", dict, EntitiesComparerTemplates.empty_dict_comparer)

boss_comparer =\
("minecraft:boss", dict, Comparer.UnnamedDictComparerSection(
    ("should_darken_sky", bool, None),
    ("hud_range", int, None),
))

breathable_comparer =\
("minecraft:breathable", dict, Comparer.UnnamedDictComparerSection(
    ("breathes_air", bool, None),
    ("breathes_water", bool, None),
    ("generates_bubbles", bool, None),
    ("suffocate_time", int, None),
    ("suffocateTime", int, None),
    ("total_supply", int, None),
    ("totalSupply", int, None),
))

breedable_comparer =\
("minecraft:breedable", dict, Comparer.UnnamedDictComparerSection(
    ("allow_sitting", bool, None),
    ("breed_items", (list, str), [
        (lambda key, value: isinstance(value, list), EntitiesComparerTemplates.item_list_comparer),
        (lambda key, value: isinstance(value, str), None),
    ]),
    ("breeds_with", (dict, list), [
        (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.baby_comparer),
        (lambda key, value: isinstance(value, list), Comparer.ListComparerSection(
            name="baby",
            ordered=False,
            types=(dict,),
            measure_length=True,
            comparer=EntitiesComparerTemplates.baby_comparer
        )),
    ]),
    ("inherit_tamed", bool, None),
    ("mutation_factor", dict, Comparer.UnnamedDictComparerSection(
        ("extra_variant", float, None),
        ("variant", float, None),
    )),
    ("mutation_strategy", str, None),
    ("parent_centric_attribute_blending", list, Comparer.ListComparerSection(
        name="attribute",
        measure_length=True,
        types=(str,),
        print_all=True,
        comparer=None,
    )),
    ("random_variant_mutation_interval", list, EntitiesComparerTemplates.range_comparer),
    ("random_extra_variant_mutation_interval", list, EntitiesComparerTemplates.range_comparer),
    ("require_full_health", bool, None),
    ("require_tame", bool, None),
))

bribeable_comparer =\
("minecraft:bribeable", dict, Comparer.UnnamedDictComparerSection(
    ("bribe_items", list, EntitiesComparerTemplates.item_list_comparer),
))

buoyant_comparer =\
("minecraft:buoyant", dict, Comparer.UnnamedDictComparerSection(
    ("apply_gravity", bool, None),
    ("base_buoyancy", float, None),
    ("drag_down_on_buoyancy_removed", float, None),
    ("big_wave_probability", float, None),
    ("big_wave_speed", float, None),
    ("liquid_blocks", list, Comparer.ListComparerSection(
        name="block",
        types=(str,),
        ordered=False,
        comparer=None,
        measure_length=True,
    )),
    ("simulate_waves", bool, None),
))

burns_in_daylight_comparer =\
("minecraft:burns_in_daylight", dict, EntitiesComparerTemplates.empty_dict_comparer)

can_climb_comparer =\
("minecraft:can_climb", dict, EntitiesComparerTemplates.empty_dict_comparer)

can_fly_comparer =\
("minecraft:can_fly", dict, EntitiesComparerTemplates.empty_dict_comparer)

can_join_raid_comparer =\
("minecraft:can_join_raid", dict, EntitiesComparerTemplates.empty_dict_comparer)

can_power_jump_comparer =\
("minecraft:can_power_jump", dict, EntitiesComparerTemplates.empty_dict_comparer)

color_comparer =\
("minecraft:color", dict, EntitiesComparerTemplates.value_comparer)

collision_box_comparer =\
("minecraft:collision_box", dict, Comparer.UnnamedDictComparerSection(
    ("height", (float, int), None),
    ("width", (float, int), None),
))

conditional_bandwidth_optimization_comparer =\
("minecraft:conditional_bandwidth_optimization", dict, Comparer.UnnamedDictComparerSection(
    ("conditional_values", list, Comparer.ListComparerSection(
        name="conditional value",
        types=(dict,),
        ordered=False,
        measure_length=True,
        comparer=EntitiesComparerTemplates.conditional_bandwidth_optimization_values_comparer
    )),
    ("default_values", dict, EntitiesComparerTemplates.conditional_bandwidth_optimization_values_comparer),
))

damage_over_time_comparer =\
("minecraft:damage_over_time", dict, Comparer.UnnamedDictComparerSection(
    ("damage_per_hurt", int, None),
    ("time_between_hurt", int, None),
))

damage_sensor_comparer =\
("minecraft:damage_sensor", dict, Comparer.UnnamedDictComparerSection(
    ("triggers", (dict, list), [
        (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.damage_sensor_triggers_comparer),
        (lambda key, value: isinstance(value, list), Comparer.ListComparerSection(
            name="trigger",
            ordered=False,
            measure_length=True,
            types=(dict,),
            comparer=EntitiesComparerTemplates.damage_sensor_triggers_comparer
        )),
    ]),
))

despawn_comparer =\
("minecraft:despawn", dict, Comparer.UnnamedDictComparerSection(
    ("despawn_from_distance", dict, Comparer.UnnamedDictComparerSection(
        ("min_distance", int, None),
        ("max_distance", int, None),
    )),
))

drying_out_timer_comparer =\
("minecraft:drying_out_timer", dict, Comparer.UnnamedDictComparerSection(
    ("dried_out_event", dict, EntitiesComparerTemplates.event_target_comparer),
    ("recover_after_dried_out_event", dict, EntitiesComparerTemplates.event_target_comparer),
    ("stopped_drying_out_event", dict, EntitiesComparerTemplates.event_target_comparer),
    ("total_time", int, None),
    ("water_bottle_refill_time", int, None),
))

dweller_comparer =\
("minecraft:dweller", dict, Comparer.UnnamedDictComparerSection(
    ("can_find_poi", bool, None),
    ("can_migrate", bool, None),
    ("dweller_role", str, None),
    ("dwelling_type", str, None),
    ("first_founding_reward", int, None),
    ("update_interval_base", int, None),
    ("update_interval_variant", int, None),
))

environment_sensor_comparer =\
("minecraft:environment_sensor", dict, Comparer.UnnamedDictComparerSection(
    ("triggers", (dict, list), [
        (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.event_target_filters_comparer),
        (lambda key, value: isinstance(value, list), Comparer.ListComparerSection(
            name="trigger",
            types=(dict,),
            measure_length=True,
            ordered=False,
            comparer=EntitiesComparerTemplates.event_target_filters_comparer
        )),
    ]),
))

equip_item_comparer =\
("minecraft:equip_item", dict, Comparer.UnnamedDictComparerSection(
    ("excluded_items", list, Comparer.ListComparerSection(
        name="item",
        ordered=False,
        measure_length=True,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("item", str, None),
        )
    )),
))

equipment_comparer =\
("minecraft:equipment", dict, Comparer.UnnamedDictComparerSection(
    ("table", str, None),
    ("slot_drop_chance", list, Comparer.ListComparerSection(
        name="slot",
        types=(dict,),
        measure_length=True,
        ordered=False,
        comparer=Comparer.UnnamedDictComparerSection(
            ("slot", str, None),
            ("drop_chance", float, None),
        )
    )),
))

eqiuppable_comparer =\
("minecraft:equippable", dict, Comparer.UnnamedDictComparerSection(
    ("slots", list, Comparer.ListComparerSection(
        name="slot",
        types=(dict,),
        measure_length=True,
        ordered=False,
        comparer=Comparer.UnnamedDictComparerSection(
            ("slot", int, None),
            ("item", str, None),
            ("accepted_items", list, EntitiesComparerTemplates.item_list_comparer),
            ("on_equip", dict, EntitiesComparerTemplates.event_target_comparer),
            ("on_unequip", dict, EntitiesComparerTemplates.event_target_comparer),
        )
    )),
))

experience_reward =\
("minecraft:experience_reward", dict, Comparer.UnnamedDictComparerSection(
    ("on_bred", str, None),
    ("on_death", str, None),
))

explode_comparer =\
("minecraft:explode", dict, Comparer.UnnamedDictComparerSection(
    ("causes_fire", bool, None),
    ("destroy_affected_by_griefing", bool, None),
    ("fire_affected_by_griefing", bool, None),
    ("fuse_length", (float, int), None),
    ("fuse_lit", bool, None),
    ("power", int, None),
))

fire_immune_comparer =\
("minecraft:fire_immune", (bool, dict), [
    (lambda key, value: isinstance(value, bool), None),
    (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.empty_dict_comparer),
])

flocking_comparer =\
("minecraft:flocking", dict, Comparer.UnnamedDictComparerSection(
    ("block_distance", float, None),
    ("block_weight", float, None),
    ("breach_influence", float, None),
    ("cohesion_threshold", float, None),
    ("cohesion_weight", float, None),
    ("goal_weight", float, None),
    ("high_flock_limit", int, None),
    ("in_water", bool, None),
    ("influence_radius", float, None),
    ("innner_cohesion_threshold", float, None),
    ("inner_cohesion_weight", float, None),
    ("loner_chance", float, None),
    ("low_flock_limit", int, None),
    ("match_variants", bool, None),
    ("max_height", float, None),
    ("min_height", float, None),
    ("separation_threshold", float, None),
    ("separation_weight", float, None),
    ("use_center_of_mass", bool, None),
))

flying_speed_comparer =\
("minecraft:flying_speed", dict, EntitiesComparerTemplates.value_comparer)

follow_range_comparer =\
("minecraft:follow_range", dict, EntitiesComparerTemplates.value_max_comparer)

game_event_movement_tracking_comparer =\
("minecraft:game_event_movement_tracking", dict, Comparer.UnnamedDictComparerSection(
    ("emit_flap", bool, None),
))

healable_comparer =\
("minecraft:healable", dict, Comparer.UnnamedDictComparerSection(
    ("items", list, Comparer.ListComparerSection(
        name="item",
        types=(dict,),
        ordered=False,
        measure_length=True,
        comparer=Comparer.UnnamedDictComparerSection(
            ("item", str, None),
            ("heal_amount", int, None),
        )
    )),
))

health_comparer =\
("minecraft:health", dict, Comparer.UnnamedDictComparerSection(
    ("max", int, None),
    ("value", (dict, int), [
        (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.range_dict_comparer),
        (lambda key, value: isinstance(value, int), None),
    ]),
))

home_comparer =\
("minecraft:home", dict, Comparer.UnnamedDictComparerSection(
    ("restriction_radius", int, None),
))

horse_jump_strength_comparer =\
("minecraft:horse.jump_strength", dict, Comparer.UnnamedDictComparerSection(
    ("value", (dict, float, int), [
        (lambda key, value: isinstance(value, (float, int)), None),
        (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.range_dict_comparer),
    ]),
))

hurt_on_condition_comparer =\
("minecraft:hurt_on_condition", dict, Comparer.UnnamedDictComparerSection(
    ("damage_conditions", list, Comparer.ListComparerSection(
        name="damage condition",
        types=(dict,),
        ordered=False,
        measure_length=True,
        comparer=Comparer.UnnamedDictComparerSection(
            ("filters", dict, EntitiesComparerTemplates.filter_comparer),
            ("cause", str, None),
            ("damage_per_tick", int, None),
        )
    )),
))

input_ground_controlled_comparer =\
("minecraft:input_ground_controlled", dict, EntitiesComparerTemplates.empty_dict_comparer)

inside_block_notifier_comparer =\
("minecraft:inside_block_notifier", dict, Comparer.UnnamedDictComparerSection(
    ("block_list", list, Comparer.ListComparerSection(
        name="block",
        types=(dict,),
        ordered=False,
        measure_length=True,
        comparer=Comparer.UnnamedDictComparerSection(
            ("block", dict, Comparer.UnnamedDictComparerSection(
                ("name", str, None),
                ("states", dict, Comparer.DictComparerSection(
                    name="state",
                    key_types=(str,),
                    value_types=(bool,),
                    measure_length=True,
                    comparer=None,
                )),
            )),
            ("entered_block_event", dict, EntitiesComparerTemplates.event_target_comparer),
            ("exited_block_event", dict, EntitiesComparerTemplates.event_target_comparer),
        )
    )),
))

interact_comparer =\
("minecraft:interact", dict, Comparer.UnnamedDictComparerSection(
    ("interactions", (dict, list), [
        (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.interaction_comparer),
        (lambda key, value: isinstance(value, list), Comparer.ListComparerSection(
            name="interaction",
            types=(dict,),
            measure_length=True,
            ordered=False,
            comparer=EntitiesComparerTemplates.interaction_comparer
        )),
    ]),
))

inventory_comparer =\
("minecraft:inventory", dict, Comparer.UnnamedDictComparerSection(
    ("inventory_size", int, None),
    ("can_be_siphoned_from", bool, None),
    ("container_type", str, None),
    ("restrict_to_owner", bool, None),
))

is_baby_comparer =\
("minecraft:is_baby", dict, EntitiesComparerTemplates.empty_dict_comparer)

is_charged_comparer =\
("minecraft:is_charged", dict, EntitiesComparerTemplates.empty_dict_comparer)

is_chested_comparer =\
("minecraft:is_chested", dict, EntitiesComparerTemplates.empty_dict_comparer)

is_dyeable_comparer =\
("minecraft:is_dyeable", dict, Comparer.UnnamedDictComparerSection(
    ("interact_text", str, None),
))

is_hidden_when_invisible =\
("minecraft:is_hidden_when_invisible", dict, EntitiesComparerTemplates.empty_dict_comparer)

is_saddled_comparer =\
("minecraft:is_saddled", dict, EntitiesComparerTemplates.empty_dict_comparer)

is_shaking_comparer =\
("minecraft:is_shaking", dict, EntitiesComparerTemplates.empty_dict_comparer)

is_stackable_comparer =\
("minecraft:is_stackable", dict, EntitiesComparerTemplates.value_comparer)

is_tamed_comparer =\
("minecraft:is_tamed", dict, EntitiesComparerTemplates.empty_dict_comparer)

item_hopper_comparer =\
("minecraft:item_hopper", dict, EntitiesComparerTemplates.empty_dict_comparer)

jump_static_comparer =\
("minecraft:jump.static", dict, Comparer.UnnamedDictComparerSection(
    ("jump_power", float, None),
))

knockback_resistance_comparer =\
("minecraft:knockback_resistance", dict, EntitiesComparerTemplates.value_max_comparer)

leashable_comparer =\
("minecraft:leashable", dict, Comparer.UnnamedDictComparerSection(
    ("soft_distance", float, None),
    ("hard_distance", float, None),
    ("max_distance", float, None),
))

lookat_comparer =\
("minecraft:lookat", dict, Comparer.UnnamedDictComparerSection(
    ("search_radius", float, None),
    ("set_target", bool, None),
    ("look_cooldown", float, None),
    ("filters", dict, EntitiesComparerTemplates.filter_comparer),
))

loot_comparer =\
("minecraft:loot", dict, Comparer.UnnamedDictComparerSection(
    ("table", str, None),
))

mark_variant_comparer =\
("minecraft:mark_variant", dict, Comparer.UnnamedDictComparerSection(
    ("value", int, None),
))

movement_comparer =\
("minecraft:movement", dict, Comparer.UnnamedDictComparerSection(
    ("max", int, None),
    ("value", (dict, float, int), [
        (lambda key, value: isinstance(value, (float, int)), None),
        (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.range_dict_comparer),
    ]),
))

movement_basic_comparer =\
("minecraft:movement.basic", dict, EntitiesComparerTemplates.empty_dict_comparer)

movement_generic_comparer =\
("minecraft:movement.generic", dict, EntitiesComparerTemplates.empty_dict_comparer)

movement_sway_comparer =\
("minecraft:movement.sway", dict, Comparer.UnnamedDictComparerSection(
    ("sway_amplitude", float, None),
))

nameable_comparer =\
("minecraft:nameable", dict, Comparer.UnnamedDictComparerSection(
    ("always_show", bool, None),
    ("allow_name_tag_renaming", bool, None),
))

navigation_comparer =\
(EntitiesComparerTemplates.get_component_key("minecraft:navigation", ["climb", "float", "generic", "walk"]), dict, Comparer.UnnamedDictComparerSection(
    ("avoid_damage_blocks", bool, None),
    ("avoid_portals", bool, None),
    ("avoid_sun", bool, None),
    ("avoid_water", bool, None),
    ("can_breach", bool, None),
    ("can_break_doors", bool, None),
    ("can_float", bool, None),
    ("can_jump", bool, None),
    ("can_open_doors", bool, None),
    ("can_pass_doors", bool, None),
    ("can_path_over_water", bool, None),
    ("can_sink", bool, None),
    ("can_swim", bool, None),
    ("can_walk", bool, None),
    ("is_amphibious", bool, None),
))

on_death_comparer =\
("minecraft:on_death", dict, EntitiesComparerTemplates.event_target_comparer)

on_hurt_comparer =\
("minecraft:on_hurt", dict, EntitiesComparerTemplates.event_target_comparer)

on_hurt_by_player_comparer =\
("minecraft:on_hurt_by_player", dict, EntitiesComparerTemplates.event_target_comparer)

on_start_landing_comparer =\
("minecraft:on_start_landing", dict, EntitiesComparerTemplates.event_target_comparer)

on_start_takeoff_comparer =\
("minecraft:on_start_takeoff", dict, EntitiesComparerTemplates.event_target_comparer)

on_target_acquired_comparer =\
("minecraft:on_target_acquired", dict, EntitiesComparerTemplates.event_target_comparer)

on_target_escape_comparer =\
("minecraft:on_target_escape", dict, EntitiesComparerTemplates.event_target_comparer)

on_wake_with_owner_comparer =\
("minecraft:on_wake_with_owner", dict, EntitiesComparerTemplates.event_target_comparer)

out_of_control_comparer =\
("minecraft:out_of_control", dict, EntitiesComparerTemplates.empty_dict_comparer)

persistent_comparer =\
("minecraft:persistent", dict, EntitiesComparerTemplates.empty_dict_comparer)

physics_comparer =\
("minecraft:physics", dict, Comparer.UnnamedDictComparerSection(
    ("has_collision", bool, None),
    ("has_gravity", bool, None),
))

preferred_path_comparer =\
("minecraft:preferred_path", dict, Comparer.UnnamedDictComparerSection(
    ("max_fall_blocks", int, None),
    ("jump_cost", int, None),
    ("default_block_cost", float, None),
    ("preferred_path_blocks", list, Comparer.ListComparerSection(
        name="block",
        ordered=False,
        measure_length=True,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("cost", int, None),
            ("blocks", list, Comparer.ListComparerSection(
                name="block",
                measure_length=True,
                ordered=False,
                types=(str,),
                comparer=None
            )),
        )
    )),
))

projectile_comparer =\
("minecraft:projectile", dict, Comparer.UnnamedDictComparerSection(
    ("anchor", int, None),
    ("angle_offset", float, None),
    ("catch_fire", bool, None),
    ("gravity", float, None),
    ("hit_water", bool, None),
    ("hit_sound", str, None), # yeah lets go wooo
    ("inertia", int, None),
    ("liquid_inertia", int, None),
    ("offset", list, EntitiesComparerTemplates.coordinate_comparer),
    ("on_hit", dict, Comparer.UnnamedDictComparerSection(
        ("arrow_effect", dict, Comparer.UnnamedDictComparerSection(
            ("apply_effect_to_blocking_targets", bool, None),
        )),
        ("definition_event", dict, Comparer.UnnamedDictComparerSection(
            ("affect_projectile", bool, None),
            ("event_trigger", dict, EntitiesComparerTemplates.event_target_comparer),
        )),
        ("douse_fire", dict, EntitiesComparerTemplates.empty_dict_comparer),
        ("freeze_on_hit", dict, Comparer.UnnamedDictComparerSection(
            ("size", float, None),
            ("shape", str, None),
            ("snap_to_block", bool, None),
        )),
        ("impact_damage", dict, Comparer.UnnamedDictComparerSection(
            *EntitiesComparerTemplates.damage_comparer
        )),
        ("particle_on_hit", dict, Comparer.UnnamedDictComparerSection(
            ("particle_type", str, None),
            ("num_particles", int, None),
            ("on_entity_hit", bool, None),
            ("on_other_hit", bool, None),
        )),
        ("remove_on_hit", dict, EntitiesComparerTemplates.empty_dict_comparer),
        ("spawn_aoe_cloud", dict, Comparer.UnnamedDictComparerSection(
            ("affect_owner", bool, None),
            ("color", list, EntitiesComparerTemplates.coordinate_comparer),
            ("duration", int, None),
            ("particle", str, None),
            ("potion", int, None),
            ("radius", float, None),
            ("radius_on_use", (float, int), None),
            ("reapplication_delay", int, None),
        )),
        ("spawn_chance", dict, Comparer.UnnamedDictComparerSection(
            ("first_spawn_chance", int, None),
            ("first_spawn_percent_chance", float, None),
            ("first_spawn_count", int, None),
            ("second_spawn_chance", int, None),
            ("second_spawn_count", int, None),
            ("spawn_baby", bool, None),
            ("spawn_definition", str, None),
        )),
        ("stick_in_ground", dict, Comparer.UnnamedDictComparerSection(
            ("shake_time", float, None),
        )),
        ("teleport_owner", dict, EntitiesComparerTemplates.empty_dict_comparer),
    )),
    ("power", float, None),
    ("reflect_on_hurt", bool, None),
    ("semi_random_diff_damage", bool, None),
    ("should_bounce", bool, None),
    ("uncertainty_base", (float, int), None),
    ("uncertainty_multiplier", int, None),
))

pushable_comparer =\
("minecraft:pushable", dict, Comparer.UnnamedDictComparerSection(
    ("is_pushable", bool, None),
    ("is_pushable_by_piston", bool, None),
))

rail_movement_comparer =\
("minecraft:rail_movement", dict, EntitiesComparerTemplates.empty_dict_comparer)

rail_sensor_comparer =\
("minecraft:rail_sensor", dict, Comparer.UnnamedDictComparerSection(
    ("check_block_types", bool, None),
    ("eject_on_activate", bool, None),
    ("eject_on_deactivate", bool, None),
    ("tick_command_block_on_activate", bool, None),
    ("tick_command_block_on_deactivate", bool, None),
    ("on_activate", dict, EntitiesComparerTemplates.event_target_filters_comparer),
    ("on_deactivate", dict, EntitiesComparerTemplates.event_target_filters_comparer),
))

rideable_comparer =\
("minecraft:rideable", dict, Comparer.UnnamedDictComparerSection(
    ("crouching_skip_interact", bool, None),
    ("family_types", list, EntitiesComparerTemplates.family_list_comparer),
    ("interact_text", str, None),
    ("passenger_max_width", float, None),
    ("priority", int, None),
    ("pull_in_entities", bool, None),
    ("seat_count", int, None),
    ("seats", (dict, list), [
        (lambda key, value: isinstance(value, list), Comparer.ListComparerSection(
            name="seat",
            ordered=True,
            types=(dict,),
            measure_length=True,
            comparer=EntitiesComparerTemplates.seat_comparer
        )),
        (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.seat_comparer),
    ]),
))

scale_comparer =\
("minecraft:scale", (bool, dict), EntitiesComparerTemplates.value_comparer)

scale_by_age_comparer =\
("minecraft:scale_by_age", dict, Comparer.UnnamedDictComparerSection(
    ("end_scale", float, None),
    ("start_scale", float, None),
))

shareables_comparer =\
("minecraft:shareables", dict, Comparer.UnnamedDictComparerSection(
    ("all_items", bool, None),
    ("all_items_max_amount", int, None),
    ("singular_pickup", bool, None),
    ("items", list, Comparer.ListComparerSection(
        name="item",
        ordered=False,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("item", str, None),
            ("max_amount", int, None),
            ("priority", int, None),
            ("surplus_amount", int, None),
            ("want_amount", int, None),
        )
    )),
))

scheduler_comparer =\
("minecraft:scheduler", dict, Comparer.UnnamedDictComparerSection(
    ("max_delay_seconds", int, None),
    ("max_delay_secs", int, None),
    ("min_delay_seconds", int, None),
    ("min_delay_secs", int, None),
    ("scheduled_events", list, Comparer.ListComparerSection(
        name="event",
        ordered=False,
        measure_length=True,
        types=(dict,),
        comparer=EntitiesComparerTemplates.event_target_filters_comparer,
    ))
))

shooter_comparer =\
("minecraft:shooter", dict, Comparer.UnnamedDictComparerSection(
    ("sound", str, None),
    ("type", str, None),
    ("def", str, None),
))

sittable_comparer =\
("minecraft:sittable", dict, EntitiesComparerTemplates.empty_dict_comparer)

spawn_entity_comparer =\
("minecraft:spawn_entity", dict, [
    (lambda key, value: "entities" in value, Comparer.UnnamedDictComparerSection(
        ("entities", dict, EntitiesComparerTemplates.spawn_entity_comparer),
    )),
    (lambda key, value: True, EntitiesComparerTemplates.spawn_entity_comparer),
])

tameable_comparer =\
("minecraft:tameable", dict, Comparer.UnnamedDictComparerSection(
    ("probability", float, None),
    ("tame_event", dict, EntitiesComparerTemplates.event_target_comparer),
    ("tame_items", list, EntitiesComparerTemplates.item_list_comparer),
))

tamemount_comparer =\
("minecraft:tamemount", dict, Comparer.UnnamedDictComparerSection(
    ("auto_reject_items", list, Comparer.ListComparerSection(
        name="item",
        ordered=False,
        types=(dict,),
        measure_length=True,
        comparer=Comparer.UnnamedDictComparerSection(
            ("item", str, None),
        )
    )),
    ("feed_items", list, Comparer.ListComparerSection(
        name="item",
        ordered=False,
        types=(dict,),
        measure_length=True,
        comparer=Comparer.UnnamedDictComparerSection(
            ("item", str, None),
            ("temper_mod", int, None),
        )
    )),
    ("feed_text", str, None),
    ("max_temper", int, None),
    ("min_temper", int, None),
    ("ride_text", str, None),
    ("tame_event", dict, EntitiesComparerTemplates.event_target_comparer),
))

target_nearby_sensor_comparer =\
("minecraft:target_nearby_sensor", dict, Comparer.UnnamedDictComparerSection(
    ("inside_range", float, None),
    ("must_see", bool, None),
    ("on_inside_range", dict, EntitiesComparerTemplates.event_target_comparer),
    ("on_outside_range", dict, EntitiesComparerTemplates.event_target_comparer),
    ("on_vision_lost_inside_range", dict, EntitiesComparerTemplates.event_target_comparer),
    ("outside_range", float, None),
))

teleport_comparer =\
("minecraft:teleport", dict, Comparer.UnnamedDictComparerSection(
    ("light_teleport_chance", float, None),
    ("max_random_teleport_time", int, None),
    ("random_teleport_cube", list, EntitiesComparerTemplates.coordinate_comparer),
    ("random_teleports", bool, None),
    ("target_distance", int, None),
    ("target_teleport_chance", float, None),
))

tick_world_comparer =\
("minecraft:tick_world", dict, EntitiesComparerTemplates.empty_dict_comparer)

timer_comparer =\
("minecraft:timer", dict, Comparer.UnnamedDictComparerSection(
    ("looping", bool, None),
    ("time", (int, list), [
        (lambda key, value: isinstance(value, int), None),
        (lambda key, value: isinstance(value, list), EntitiesComparerTemplates.range_comparer),
    ]),
    ("time_down_event", dict, EntitiesComparerTemplates.event_target_comparer),
))

transformation_comparer =\
("minecraft:transformation", dict, Comparer.UnnamedDictComparerSection(
    ("into", str, None),
    ("transformation_sound", str, None),
    ("drop_equipment", bool, None),
    ("delay", (dict, float), [
        (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.value_comparer),
        (lambda key, value: isinstance(value, float), None),
    ]),
))

trust_comparer =\
("minecraft:trust", dict, EntitiesComparerTemplates.empty_dict_comparer)

type_family_comparer =\
("minecraft:type_family", dict, Comparer.UnnamedDictComparerSection(
    ("family", list, EntitiesComparerTemplates.family_list_comparer),
))

underwater_movement_comparer =\
("minecraft:underwater_movement", dict, EntitiesComparerTemplates.value_comparer)

variable_max_auto_step_comparer =\
("minecraft:variable_max_auto_step", dict, Comparer.UnnamedDictComparerSection(
    ("base_value", float, None),
    ("jump_prevented_value", float, None),
))

variant_comparer =\
("minecraft:variant", dict, EntitiesComparerTemplates.value_comparer)

components_comparer_types = [
    addrider_comparer,
    ageable_comparer,
    ambient_sound_interval_comparer,
    angry_comparer,
    annotation_break_door_comparer,
    attack_comparer,
    attack_damage_comparer,
    balloon_comparer,
    balloonable_comparer,
    block_climber_comparer,
    boss_comparer,
    breathable_comparer,
    breedable_comparer,
    bribeable_comparer,
    buoyant_comparer,
    burns_in_daylight_comparer,
    can_climb_comparer,
    can_fly_comparer,
    can_join_raid_comparer,
    can_power_jump_comparer,
    color_comparer,
    collision_box_comparer,
    conditional_bandwidth_optimization_comparer,
    damage_over_time_comparer,
    damage_sensor_comparer,
    despawn_comparer,
    drying_out_timer_comparer,
    dweller_comparer,
    environment_sensor_comparer,
    equip_item_comparer,
    equipment_comparer,
    eqiuppable_comparer,
    experience_reward,
    explode_comparer,
    fire_immune_comparer,
    flocking_comparer,
    flying_speed_comparer,
    follow_range_comparer,
    game_event_movement_tracking_comparer,
    healable_comparer,
    health_comparer,
    home_comparer,
    horse_jump_strength_comparer,
    hurt_on_condition_comparer,
    input_ground_controlled_comparer,
    inside_block_notifier_comparer,
    interact_comparer,
    inventory_comparer,
    is_baby_comparer,
    is_charged_comparer,
    is_chested_comparer,
    is_dyeable_comparer,
    is_hidden_when_invisible,
    is_saddled_comparer,
    is_shaking_comparer,
    is_stackable_comparer,
    is_tamed_comparer,
    item_hopper_comparer,
    jump_static_comparer,
    knockback_resistance_comparer,
    leashable_comparer,
    lookat_comparer,
    loot_comparer,
    mark_variant_comparer,
    movement_comparer,
    movement_basic_comparer,
    movement_generic_comparer,
    movement_sway_comparer,
    nameable_comparer,
    navigation_comparer,
    on_death_comparer,
    on_hurt_comparer,
    on_hurt_by_player_comparer,
    on_start_landing_comparer,
    on_start_takeoff_comparer,
    on_target_acquired_comparer,
    on_target_escape_comparer,
    on_wake_with_owner_comparer,
    out_of_control_comparer,
    persistent_comparer,
    physics_comparer,
    preferred_path_comparer,
    projectile_comparer,
    pushable_comparer,
    rail_movement_comparer,
    rail_sensor_comparer,
    rideable_comparer,
    scale_comparer,
    scale_by_age_comparer,
    shareables_comparer,
    scheduler_comparer,
    shooter_comparer,
    sittable_comparer,
    spawn_entity_comparer,
    tameable_comparer,
    tamemount_comparer,
    target_nearby_sensor_comparer,
    teleport_comparer,
    tick_world_comparer,
    timer_comparer,
    transformation_comparer,
    trust_comparer,
    type_family_comparer,
    underwater_movement_comparer,
    variable_max_auto_step_comparer,
    variant_comparer,
]

components_comparer_types.extend(EntitiesComparerBehaviors.comparers)

comparer = Comparer.UnnamedDictComparerSection(
    *components_comparer_types,
    name="component"
)
