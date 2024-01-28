import Comparison.Comparer as Comparer

import DataMiners.Entities.EntitiesComparerBehaviors as EntitiesComparerBehaviors
import DataMiners.Entities.EntitiesComparerTemplates as EntitiesComparerTemplates

decimal = float|int

addrider_comparer =\
("minecraft:addrider", dict, Comparer.UnnamedDictComparerSection(
    ("entity_type", str, None),
    ("spawn_event", str, None),
))

admire_item_comparer =\
("minecraft:admire_item", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_after_being_attacked", int, None),
    ("duration", int, None),
))

ageable_comparer =\
("minecraft:ageable", dict, Comparer.UnnamedDictComparerSection(
    ("drop_items", list, EntitiesComparerTemplates.item_list_comparer),
    ("duration", int, None),
    ("feed_items", (list, str), [
        (lambda key, value: isinstance(value, list) and (len(value) == 0 or isinstance(value[0], str)), EntitiesComparerTemplates.item_list_comparer),
        (lambda key, value: isinstance(value, list) and isinstance(value[0], dict), Comparer.ListComparerSection(
            name="item",
            types=(dict,),
            ordered=False,
            measure_length=True,
            comparer=Comparer.UnnamedDictComparerSection(
                ("growth", decimal, None),
                ("item", str, None),
            )
        )),
        (lambda key, value: isinstance(value, str), None),
    ]),
    ("grow_up", dict, EntitiesComparerTemplates.event_target_comparer),
    ("interact_filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("transform_to_item", str, None),
))

ambient_sound_interval_comparer =\
("minecraft:ambient_sound_interval", dict, Comparer.UnnamedDictComparerSection(
    ("event_name", str, None),
    ("event_names", list, Comparer.ListComparerSection(
        name="event",
        measure_length=True,
        ordered=False,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("event_name", str, None),
            ("condition", str, None),
        )
    )),
    ("range", decimal, None),
    ("value", decimal, None),
))

anger_level_comparer =\
("minecraft:anger_level", dict, Comparer.UnnamedDictComparerSection(
    ("anger_decrement_interval", decimal, None),
    ("angry_boost", int, None),
    ("angry_threshold", int, None),
    ("default_annoyingness", int, None),
    ("default_projectile_annoyingness", int, None),
    ("max_anger", int, None),
    ("nuisance_filter", dict, EntitiesComparerTemplates.filter_comparer),
    ("on_increase_sounds", list, Comparer.ListComparerSection(
        name="sound",
        ordered=False,
        measure_length=True,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("condition", str, None),
            ("sound", str, None),
        )
    )),
    ("remove_targets_below_angry_threshold", bool, None),
))

angry_comparer =\
("minecraft:angry", dict, Comparer.UnnamedDictComparerSection(
    ("angry_sound", str, None),
    ("broadcast_anger", bool, None),
    ("broadcast_anger_on_attack", bool, None),
    ("broadcast_anger_on_being_attacked", bool, None),
    ("broadcast_filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("broadcast_range", int, None),
    ("broadcast_targets", list, Comparer.ListComparerSection(
        name="entity",
        measure_length=True,
        ordered=False,
        types=(str,),
        comparer=None
    )),
    ("broadcastAnger", bool, None),
    ("broadcastRange", int, None),
    ("calm_event", dict, EntitiesComparerTemplates.event_target_comparer),
    ("duration", int, None),
    ("duration_delta", int, None),
    ("filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("sound_interval", dict, EntitiesComparerTemplates.range_dict_comparer),
))

annotation_break_door_comparer =\
("minecraft:annotation.break_door", dict, Comparer.UnnamedDictComparerSection(
    ("break_time", int, None),
    ("min_difficulty", str, None),
))

annotation_open_door_comparer =\
("minecraft:annotation.open_door", dict, EntitiesComparerTemplates.empty_dict_comparer)

area_attack_comparer =\
("minecraft:area_attack", dict, Comparer.UnnamedDictComparerSection(
    ("cause", str, None),
    ("damage_cooldown", decimal, None),
    ("damage_per_tick", int, None),
    ("damage_range", decimal, None),
    ("entity_filter", dict, EntitiesComparerTemplates.filter_comparer),
))

attack_comparer =\
("minecraft:attack", dict, Comparer.UnnamedDictComparerSection(
    *EntitiesComparerTemplates.damage_comparer
))

attack_cooldown_comparer =\
("minecraft:attack_cooldown", dict, Comparer.UnnamedDictComparerSection(
    ("attack_cooldown_complete_event", dict, EntitiesComparerTemplates.event_target_comparer),
    ("attack_cooldown_time", (decimal, list), [
        (lambda key, value: isinstance(value, decimal), None),
        (lambda key, value: isinstance(value, list), EntitiesComparerTemplates.range_comparer),
    ]),
))

attack_damage_comparer =\
("minecraft:attack_damage", dict, EntitiesComparerTemplates.value_comparer)

balloon_comparer =\
("minecraft:balloon", dict, Comparer.UnnamedDictComparerSection(
    ("lift_force", list, EntitiesComparerTemplates.coordinate_comparer),
))

balloonable_comparer =\
("minecraft:balloonable", dict, Comparer.UnnamedDictComparerSection(
    ("mass", decimal, None),
))

barter_comparer =\
("minecraft:barter", dict, Comparer.UnnamedDictComparerSection(
    ("barter_table", str, None),
    ("cooldown_after_being_attacked", int, None),
))

block_climber_comparer =\
("minecraft:block_climber", dict, EntitiesComparerTemplates.empty_dict_comparer)

block_sensor_comparer =\
("minecraft:block_sensor", dict, Comparer.UnnamedDictComparerSection(
    ("on_break", list, Comparer.ListComparerSection(
        name="event",
        ordered=False,
        measure_length=True,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("block_list", list, EntitiesComparerTemplates.block_list_comparer),
            ("on_block_broken", str, None),
        )
    )),
    ("sensor_radius", int, None),
    ("sources", list, EntitiesComparerTemplates.filter_list_comparer)
))

boostable_comparer =\
("minecraft:boostable", dict, Comparer.UnnamedDictComparerSection(
    ("boost_items", list, Comparer.ListComparerSection(
        name="item",
        measure_length=True,
        ordered=False,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("damage", int, None),
            ("item", str, None),
            ("replace_item", str, None),
        )
    )),
    ("duration", decimal, None),
    ("speed_multiplier", decimal, None),
))

boss_comparer =\
("minecraft:boss", dict, Comparer.UnnamedDictComparerSection(
    ("should_darken_sky", bool, None),
    ("hud_range", int, None),
))

break_blocks_comparer =\
("minecraft:break_blocks", dict, Comparer.UnnamedDictComparerSection(
    ("breakable_blocks", list, EntitiesComparerTemplates.block_list_comparer),
))

breathable_comparer =\
("minecraft:breathable", dict, Comparer.UnnamedDictComparerSection(
    ("breathes_air", bool, None),
    ("breathes_lava", bool, None),
    ("breathes_water", bool, None),
    ("generates_bubbles", bool, None),
    ("inhale_time", decimal, None),
    ("suffocate_time", int, None),
    ("suffocateTime", int, None),
    ("total_supply", int, None),
    ("totalSupply", int, None),
))

breedable_comparer =\
("minecraft:breedable", dict, Comparer.UnnamedDictComparerSection(
    ("allow_sitting", bool, None),
    ("blend_attributes", bool, None),
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
    ("causes_pregnancy", bool, None),
    ("deny_parents_variant", dict, Comparer.UnnamedDictComparerSection(
        ("chance", decimal, None),
        ("max_variant", int, None),
        ("min_variant", int, None),
    )),
    ("environment_requirements", dict, Comparer.UnnamedDictComparerSection(
        ("blocks", str, None),
        ("count", int, None),
        ("radius", int, None),
    )),
    ("inherit_tamed", bool, None),
    ("love_filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("mutation_factor", dict, Comparer.UnnamedDictComparerSection(
        ("extra_variant", decimal, None),
        ("variant", decimal, None),
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
    ("transform_to_item", str, None),
))

bribeable_comparer =\
("minecraft:bribeable", dict, Comparer.UnnamedDictComparerSection(
    ("bribe_items", list, EntitiesComparerTemplates.item_list_comparer),
))

buoyant_comparer =\
("minecraft:buoyant", dict, Comparer.UnnamedDictComparerSection(
    ("apply_gravity", bool, None),
    ("base_buoyancy", decimal, None),
    ("drag_down_on_buoyancy_removed", decimal, None),
    ("big_wave_probability", decimal, None),
    ("big_wave_speed", decimal, None),
    ("liquid_blocks", list, EntitiesComparerTemplates.block_list_comparer),
    ("simulate_waves", bool, None),
))

burns_in_daylight_comparer =\
("minecraft:burns_in_daylight", (bool, dict), [
    (lambda key, value: isinstance(value, bool), None),
    (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.empty_dict_comparer),
])

can_climb_comparer =\
("minecraft:can_climb", dict, EntitiesComparerTemplates.empty_dict_comparer)

can_fly_comparer =\
("minecraft:can_fly", dict, EntitiesComparerTemplates.empty_dict_comparer)

can_join_raid_comparer =\
("minecraft:can_join_raid", dict, EntitiesComparerTemplates.empty_dict_comparer)

can_power_jump_comparer =\
("minecraft:can_power_jump", dict, EntitiesComparerTemplates.empty_dict_comparer)

celebrate_hunt_comparer =\
("minecraft:celebrate_hunt", dict, Comparer.UnnamedDictComparerSection(
    ("broadcast", bool, None),
    ("celebrate_sound", str, None),
    ("celebration_targets", dict, EntitiesComparerTemplates.filter_comparer),
    ("duration", int, None),
    ("radius", int, None),
    ("sound_interval", dict, EntitiesComparerTemplates.range_dict_comparer),
))

color_comparer =\
("minecraft:color", dict, EntitiesComparerTemplates.value_comparer)

color2_comparer =\
("minecraft:color2", dict, EntitiesComparerTemplates.value_comparer)

collision_box_comparer =\
("minecraft:collision_box", dict, Comparer.UnnamedDictComparerSection(
    ("height", decimal, None),
    ("width", decimal, None),
))

combat_regeneration_comparer =\
("minecraft:combat_regeneration", dict, EntitiesComparerTemplates.empty_dict_comparer)

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

custom_hit_test_comparer =\
("minecraft:custom_hit_test", dict, Comparer.UnnamedDictComparerSection(
    ("hitboxes", list, Comparer.ListComparerSection(
        name="hitbox",
        ordered=False,
        measure_length=True,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("pivot", list, EntitiesComparerTemplates.coordinate_comparer),
            ("height", decimal, None),
            ("width", decimal, None),
        )
    )),
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

dash_comparer =\
("minecraft:dash", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_time", decimal, None),
    ("horizontal_momentum", decimal, None),
    ("vertical_momentum", decimal, None),
))

delayed_attack =\
("minecraft:behavior.delayed_attack", dict, Comparer.UnnamedDictComparerSection(
    ("attack_duration", decimal, None),
    ("attack_once", bool, None),
    ("hit_delay_pct", decimal, None),
    ("priority", int, None),
    ("random_stop_interval", int, None),
    ("reach_multiplier", decimal, None),
    ("require_complete_path", bool, None),
    ("speed_multiplier", decimal, None),
    ("track_target", bool, None),
))

despawn_comparer =\
("minecraft:despawn", dict, Comparer.UnnamedDictComparerSection(
    ("despawn_from_distance", dict, Comparer.UnnamedDictComparerSection(
        ("min_distance", int, None),
        ("max_distance", int, None),
    )),
    ("filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("remove_child_entities", bool, None),
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
    ("preferred_profession", str, None),
    ("update_interval_base", int, None),
    ("update_interval_variant", int, None),
))

eat_block_comparer =\
("minecraft:behavior.eat_block", dict, Comparer.UnnamedDictComparerSection(
    ("eat_and_replace_block_pairs", list, Comparer.ListComparerSection(
        name="block pair",
        measure_length=True,
        ordered=False,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("eat_block", str, None),
            ("replace_block", str, None),
        )
    )),
    ("on_eat", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("success_chance", str, None),
    ("time_until_eat", decimal, None),
))

economy_trade_table_comparer =\
("minecraft:economy_trade_table", dict, Comparer.UnnamedDictComparerSection(
    ("cured_discount", list, EntitiesComparerTemplates.range_comparer),
    ("display_name", str, None),
    ("max_cured_discount", list, EntitiesComparerTemplates.range_comparer),
    ("new_screen", bool, None),
    ("persist_trades", bool, None),
    ("table", str, None),
))

entity_sensor_comparer = EntitiesComparerTemplates.entity_sensor_comparer

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
            ("drop_chance", decimal, None),
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

exhaustion_values_comparer =\
("minecraft:exhaustion_values", dict, Comparer.UnnamedDictComparerSection(
    ("attack", decimal, None),
    ("damage", decimal, None),
    ("heal", decimal, None),
    ("jump", decimal, None),
    ("mine", decimal, None),
    ("sprint", decimal, None),
    ("sprint_jump", decimal, None),
    ("swim", decimal, None),
    ("walk", decimal, None),
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
    ("fuse_length", (dict, decimal), [
        (lambda key, value: isinstance(value, decimal), None),
        (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.range_dict_comparer),
    ]),
    ("fuse_lit", bool, None),
    ("max_resistance", decimal, None),
    ("power", int, None),
))

fire_immune_comparer =\
("minecraft:fire_immune", (bool, dict), [
    (lambda key, value: isinstance(value, bool), None),
    (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.empty_dict_comparer),
])

flocking_comparer =\
("minecraft:flocking", dict, Comparer.UnnamedDictComparerSection(
    ("block_distance", decimal, None),
    ("block_weight", decimal, None),
    ("breach_influence", decimal, None),
    ("cohesion_threshold", decimal, None),
    ("cohesion_weight", decimal, None),
    ("goal_weight", decimal, None),
    ("high_flock_limit", int, None),
    ("in_water", bool, None),
    ("influence_radius", decimal, None),
    ("innner_cohesion_threshold", decimal, None),
    ("inner_cohesion_weight", decimal, None),
    ("loner_chance", decimal, None),
    ("low_flock_limit", int, None),
    ("match_variants", bool, None),
    ("max_height", decimal, None),
    ("min_height", decimal, None),
    ("separation_threshold", decimal, None),
    ("separation_weight", decimal, None),
    ("use_center_of_mass", bool, None),
))

flying_speed_comparer =\
("minecraft:flying_speed", dict, EntitiesComparerTemplates.value_comparer)

follow_range_comparer =\
("minecraft:follow_range", (dict, int), [
    (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.value_max_comparer),
    (lambda key, value: isinstance(value, int), None),
])

game_event_movement_tracking_comparer =\
("minecraft:game_event_movement_tracking", dict, Comparer.UnnamedDictComparerSection(
    ("emit_flap", bool, None),
    ("emit_move", bool, None),
    ("emit_swim", bool, None),
))

genetics_comparer =\
("minecraft:genetics", dict, Comparer.UnnamedDictComparerSection(
    ("genes", list, Comparer.ListComparerSection(
        name="gene",
        measure_length=True,
        ordered=False,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("allele_range", dict, EntitiesComparerTemplates.range_dict_comparer),
            ("genetic_variants", list, Comparer.ListComparerSection(
                name="genetic variant",
                ordered=False,
                measure_length=True,
                types=(dict,),
                comparer=Comparer.UnnamedDictComparerSection(
                    ("birth_event", dict, EntitiesComparerTemplates.event_target_comparer),
                    ("both_allele", dict, EntitiesComparerTemplates.range_dict_comparer),
                    ("main_allele", (dict, int), [
                        (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.range_dict_comparer),
                        (lambda key, value: isinstance(value, int), None),
                    ]),
                )
            )),
            ("name", str, None),
            ("use_simplified_breeding", bool, None),
        )
    )),
    ("mutation_rate", decimal, None),
))

giveable_comparer =\
("minecraft:giveable", dict, Comparer.UnnamedDictComparerSection(
    ("triggers", dict, Comparer.UnnamedDictComparerSection(
        ("cooldown", decimal, None),
        ("items", list, EntitiesComparerTemplates.item_list_comparer),
        ("on_give", dict, EntitiesComparerTemplates.event_target_comparer),
    )),
))

group_size_comparer =\
("minecraft:group_size", dict, Comparer.UnnamedDictComparerSection(
    ("filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("radius", int, None),
))

grows_crop_comparer =\
("minecraft:grows_crop", dict, Comparer.UnnamedDictComparerSection(
    ("chance", decimal, None),
    ("charges", int, None),
))

healable_comparer =\
("minecraft:healable", dict, Comparer.UnnamedDictComparerSection(
    ("filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("force_use", bool, None),
    ("items", list, Comparer.ListComparerSection(
        name="item",
        types=(dict,),
        ordered=False,
        measure_length=True,
        comparer=Comparer.UnnamedDictComparerSection(
            ("effects", list, Comparer.ListComparerSection(
                name="effect",
                ordered=False,
                measure_length=True,
                types=(dict,),
                comparer=Comparer.UnnamedDictComparerSection(
                    ("amplifier", int, None),
                    ("chance", decimal, None),
                    ("duration", int, None),
                    ("name", str, None),
                )
            )),
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

heartbeat_comparer =\
("minecraft:heartbeat", dict, Comparer.UnnamedDictComparerSection(
    ("interval", str, None),
))

hide_comparer =\
("minecraft:hide", dict, EntitiesComparerTemplates.empty_dict_comparer)

home_comparer =\
("minecraft:home", dict, Comparer.UnnamedDictComparerSection(
    ("home_block_list", list, EntitiesComparerTemplates.block_list_comparer),
    ("restriction_radius", int, None),
))

horse_jump_strength_comparer =\
("minecraft:horse.jump_strength", dict, Comparer.UnnamedDictComparerSection(
    ("value", (dict, decimal), [
        (lambda key, value: isinstance(value, decimal), None),
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

insomnia_comparer =\
("minecraft:insomnia", dict, Comparer.UnnamedDictComparerSection(
    ("days_until_insomnia", int, None),
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
    ("additional_slots_per_strength", int, None),
    ("inventory_size", int, None),
    ("can_be_siphoned_from", bool, None),
    ("container_type", str, None),
    ("private", bool, None),
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

is_ignited_comparer =\
("minecraft:is_ignited", dict, EntitiesComparerTemplates.empty_dict_comparer)

is_illager_captain_comparer =\
("minecraft:is_illager_captain", dict, EntitiesComparerTemplates.empty_dict_comparer)

is_pregnant_comparer =\
("minecraft:is_pregnant", dict, EntitiesComparerTemplates.empty_dict_comparer)

is_saddled_comparer =\
("minecraft:is_saddled", dict, EntitiesComparerTemplates.empty_dict_comparer)

is_shaking_comparer =\
("minecraft:is_shaking", dict, EntitiesComparerTemplates.empty_dict_comparer)

is_sheared_comparer =\
("minecraft:is_sheared", dict, EntitiesComparerTemplates.empty_dict_comparer)

is_stackable_comparer =\
("minecraft:is_stackable", dict, EntitiesComparerTemplates.value_comparer)

is_stunned_comparer =\
("minecraft:is_stunned", dict, EntitiesComparerTemplates.empty_dict_comparer)

is_tamed_comparer =\
("minecraft:is_tamed", dict, EntitiesComparerTemplates.empty_dict_comparer)

item_controllable_comparer =\
("minecraft:item_controllable", dict, Comparer.UnnamedDictComparerSection(
    ("control_items", str, None),
))

item_hopper_comparer =\
("minecraft:item_hopper", dict, EntitiesComparerTemplates.empty_dict_comparer)

jump_dynamic_comparer =\
("minecraft:jump.dynamic", dict, EntitiesComparerTemplates.empty_dict_comparer)

jump_static_comparer =\
("minecraft:jump.static", dict, Comparer.UnnamedDictComparerSection(
    ("jump_power", decimal, None),
))

knockback_resistance_comparer =\
("minecraft:knockback_resistance", dict, EntitiesComparerTemplates.value_max_comparer)

lava_movement_comparer =\
("minecraft:lava_movement", dict, EntitiesComparerTemplates.value_comparer)

leashable_comparer =\
("minecraft:leashable", dict, Comparer.UnnamedDictComparerSection(
    ("can_be_stolen", bool, None),
    ("hard_distance", decimal, None),
    ("max_distance", decimal, None),
    ("on_leash", dict, EntitiesComparerTemplates.event_target_comparer),
    ("on_unleash", dict, EntitiesComparerTemplates.event_target_comparer),
    ("soft_distance", decimal, None),
))

lookat_comparer =\
("minecraft:lookat", dict, Comparer.UnnamedDictComparerSection(
    ("search_radius", decimal, None),
    ("set_target", bool, None),
    ("look_cooldown", decimal, None),
    ("filters", dict, EntitiesComparerTemplates.filter_comparer),
))

loot_comparer =\
("minecraft:loot", dict, Comparer.UnnamedDictComparerSection(
    ("table", str, None),
))

managed_wandering_trader_comparer =\
("minecraft:managed_wandering_trader", dict, EntitiesComparerTemplates.empty_dict_comparer)

mark_variant_comparer =\
("minecraft:mark_variant", dict, Comparer.UnnamedDictComparerSection(
    ("value", int, None),
))

mob_effect_comparer =\
("minecraft:mob_effect", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_time", int, None),
    ("effect_range", decimal, None),
    ("effect_time", int, None),
    ("entity_filter", dict, EntitiesComparerTemplates.filter_comparer),
    ("mob_effect", str, None),
))

movement_comparer =\
("minecraft:movement", dict, Comparer.UnnamedDictComparerSection(
    ("max", decimal, None),
    ("value", (dict, decimal), [
        (lambda key, value: isinstance(value, decimal), None),
        (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.range_dict_comparer),
    ]),
))

movement_amphibious_comparer =\
("minecraft:movement.amphibious", dict, Comparer.UnnamedDictComparerSection(
    ("max_turn", decimal, None),
))

movement_basic_comparer =\
("minecraft:movement.basic", dict, Comparer.UnnamedDictComparerSection(
    ("max_turn", decimal, None),
))

movement_fly_comparer =\
("minecraft:movement.fly", dict, EntitiesComparerTemplates.empty_dict_comparer)

movement_generic_comparer =\
("minecraft:movement.generic", dict, EntitiesComparerTemplates.empty_dict_comparer)

movement_glide_comparer =\
("minecraft:movement.glide", dict, Comparer.UnnamedDictComparerSection(
    ("start_speed", decimal, None),
    ("speed_when_turning", decimal, None),
))

movement_hover_comparer =\
("minecraft:movement.hover", dict, EntitiesComparerTemplates.empty_dict_comparer)

movement_jump_comparer =\
("minecraft:movement.jump", dict, Comparer.UnnamedDictComparerSection(
    ("jump_delay", list, EntitiesComparerTemplates.range_comparer),
))

movement_skip_comparer =\
("minecraft:movement.skip", dict, EntitiesComparerTemplates.empty_dict_comparer)

movement_sway_comparer =\
("minecraft:movement.sway", dict, Comparer.UnnamedDictComparerSection(
    ("sway_amplitude", decimal, None),
))

movement_sound_distance_offset_comparer =\
("minecraft:movement_sound_distance_offset", dict, EntitiesComparerTemplates.value_comparer)

nameable_comparer =\
("minecraft:nameable", dict, Comparer.UnnamedDictComparerSection(
    ("allow_name_tag_renaming", bool, None),
    ("always_show", bool, None),
    ("default_trigger", dict, EntitiesComparerTemplates.event_target_comparer),
    ("name_actions", list, Comparer.ListComparerSection(
        name="action",
        ordered=False,
        measure_length=True,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("name_filter", str, None),
            ("on_named", dict, EntitiesComparerTemplates.event_target_comparer),
        )
    ))
))

navigation_comparer =\
(EntitiesComparerTemplates.get_component_key("minecraft:navigation", ["climb", "float", "fly", "generic", "hover", "walk"]), dict, Comparer.UnnamedDictComparerSection(
    ("avoid_damage_blocks", bool, None),
    ("avoid_portals", bool, None),
    ("avoid_sun", bool, None),
    ("avoid_water", bool, None),
    ("blocks_to_avoid", list, Comparer.ListComparerSection(
        name="block",
        measure_length=True,
        ordered=False,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("name", str, None),
            ("tags", str, None),
        )
    )),
    ("can_breach", bool, None),
    ("can_break_doors", bool, None),
    ("can_float", bool, None),
    ("can_jump", bool, None),
    ("can_open_doors", bool, None),
    ("can_pass_doors", bool, None),
    ("can_path_from_air", bool, None),
    ("can_path_over_lava", bool, None),
    ("can_path_over_water", bool, None),
    ("can_sink", bool, None),
    ("can_swim", bool, None),
    ("can_walk", bool, None),
    ("can_walk_in_lava", bool, None),
    ("is_amphibious", bool, None),
))

npc_comparer =\
("minecraft:npc", dict, Comparer.UnnamedDictComparerSection(
    ("npc_data", dict, Comparer.UnnamedDictComparerSection(
        ("picker_offsets", dict, Comparer.UnnamedDictComparerSection(
            ("scale", list, EntitiesComparerTemplates.coordinate_comparer),
            ("translate", list, EntitiesComparerTemplates.coordinate_comparer),
        )),
        ("portrait_offsets", dict, Comparer.UnnamedDictComparerSection(
            ("scale", list, EntitiesComparerTemplates.coordinate_comparer),
            ("translate", list, EntitiesComparerTemplates.coordinate_comparer),
        )),
        ("skin_list", list, Comparer.ListComparerSection(
            name="skin",
            ordered=False,
            measure_length=True,
            types=(dict,),
            comparer=Comparer.UnnamedDictComparerSection(
                ("variant", int, None),
            )
        )),
    )),
))

on_death_comparer =\
("minecraft:on_death", dict, EntitiesComparerTemplates.event_target_comparer)

on_friendly_anger =\
("minecraft:on_friendly_anger", dict, EntitiesComparerTemplates.event_target_comparer)

on_hurt_comparer =\
("minecraft:on_hurt", dict, EntitiesComparerTemplates.event_target_comparer)

on_hurt_by_player_comparer =\
("minecraft:on_hurt_by_player", dict, EntitiesComparerTemplates.event_target_comparer)

on_start_landing_comparer =\
("minecraft:on_start_landing", dict, EntitiesComparerTemplates.event_target_comparer)

on_start_takeoff_comparer =\
("minecraft:on_start_takeoff", dict, EntitiesComparerTemplates.event_target_comparer)

on_target_acquired_comparer =\
("minecraft:on_target_acquired", dict, EntitiesComparerTemplates.event_target_filters_comparer)

on_target_escape_comparer =\
("minecraft:on_target_escape", dict, EntitiesComparerTemplates.event_target_filters_comparer)

on_wake_with_owner_comparer =\
("minecraft:on_wake_with_owner", dict, EntitiesComparerTemplates.event_target_comparer)

out_of_control_comparer =\
("minecraft:out_of_control", dict, EntitiesComparerTemplates.empty_dict_comparer)

peek_comparer =\
("minecraft:peek", dict, Comparer.UnnamedDictComparerSection(
    ("on_close", dict, EntitiesComparerTemplates.event_target_comparer),
    ("on_open", dict, EntitiesComparerTemplates.event_target_comparer),
    ("on_target_open", dict, EntitiesComparerTemplates.event_target_comparer),
))

persistent_comparer =\
("minecraft:persistent", dict, EntitiesComparerTemplates.empty_dict_comparer)

physics_comparer =\
("minecraft:physics", dict, Comparer.UnnamedDictComparerSection(
    ("has_collision", bool, None),
    ("has_gravity", bool, None),
    ("push_towards_closest_space", bool, None),
))

player_exhaustion_comparer =\
("minecraft:player.exhaustion", dict, EntitiesComparerTemplates.value_max_comparer)

player_experience_comparer =\
("minecraft:player.experience", dict, EntitiesComparerTemplates.value_max_comparer)

player_level_comparer =\
("minecraft:player.level", dict, EntitiesComparerTemplates.value_max_comparer)

player_saturation_comparer =\
("minecraft:player.saturation", dict, EntitiesComparerTemplates.value_max_comparer)

preferred_path_comparer =\
("minecraft:preferred_path", dict, Comparer.UnnamedDictComparerSection(
    ("max_fall_blocks", int, None),
    ("jump_cost", int, None),
    ("default_block_cost", decimal, None),
    ("preferred_path_blocks", list, Comparer.ListComparerSection(
        name="block",
        ordered=False,
        measure_length=True,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("cost", int, None),
            ("blocks", list, EntitiesComparerTemplates.block_list_comparer),
        )
    )),
))

projectile_comparer =\
("minecraft:projectile", dict, Comparer.UnnamedDictComparerSection(
    ("anchor", int, None),
    ("angle_offset", decimal, None),
    ("catch_fire", bool, None),
    ("crit_particle_on_hurt", bool, None),
    ("destroyOnHurt", bool, None),
    ("gravity", decimal, None),
    ("homing", bool, None),
    ("hit_ground_sound", str, None), # woohooooo
    ("hit_sound", str, None), # yeah lets go wooo
    ("hit_water", bool, None),
    ("inertia", decimal, None),
    ("is_dangerous", bool, None),
    ("liquid_inertia", decimal, None),
    ("multiple_targets", bool, None),
    ("offset", list, EntitiesComparerTemplates.coordinate_comparer),
    ("on_hit", dict, Comparer.UnnamedDictComparerSection(
        ("arrow_effect", dict, Comparer.UnnamedDictComparerSection(
            ("apply_effect_to_blocking_targets", bool, None),
        )),
        ("catch_fire", dict, Comparer.UnnamedDictComparerSection(
            ("fire_affected_by_griefing", bool, None),
        )),
        ("definition_event", dict, Comparer.UnnamedDictComparerSection(
            ("affect_projectile", bool, None),
            ("event_trigger", dict, EntitiesComparerTemplates.event_target_comparer),
        )),
        ("douse_fire", dict, EntitiesComparerTemplates.empty_dict_comparer),
        ("freeze_on_hit", dict, Comparer.UnnamedDictComparerSection(
            ("size", decimal, None),
            ("shape", str, None),
            ("snap_to_block", bool, None),
        )),
        ("grant_xp", dict, Comparer.UnnamedDictComparerSection(
            ("maxXP", int, None),
            ("minXP", int, None),
        )),
        ("impact_damage", dict, Comparer.UnnamedDictComparerSection(
            *EntitiesComparerTemplates.damage_comparer
        )),
        ("mob_effect", dict, Comparer.UnnamedDictComparerSection(
            ("amplifier", int, None),
            ("durationeasy", int, None),
            ("durationhard", int, None),
            ("durationnormal", int, None),
            ("effect", str, None),
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
            ("radius", decimal, None),
            ("radius_on_use", decimal, None),
            ("reapplication_delay", int, None),
        )),
        ("spawn_chance", dict, Comparer.UnnamedDictComparerSection(
            ("first_spawn_chance", int, None),
            ("first_spawn_percent_chance", decimal, None),
            ("first_spawn_count", int, None),
            ("second_spawn_chance", int, None),
            ("second_spawn_count", int, None),
            ("spawn_baby", bool, None),
            ("spawn_definition", str, None),
        )),
        ("stick_in_ground", dict, Comparer.UnnamedDictComparerSection(
            ("shake_time", decimal, None),
        )),
        ("teleport_owner", dict, EntitiesComparerTemplates.empty_dict_comparer),
        ("thrown_potion_effect", dict, EntitiesComparerTemplates.empty_dict_comparer),
    )),
    ("power", decimal, None),
    ("reflect_on_hurt", bool, None),
    ("semi_random_diff_damage", bool, None),
    ("shoot_sound", str, None),
    ("shoot_target", bool, None),
    ("should_bounce", bool, None),
    ("stop_on_hurt", bool, None),
    ("uncertainty_base", decimal, None),
    ("uncertainty_multiplier", decimal, None),
))

pushable_comparer =\
("minecraft:pushable", dict, Comparer.UnnamedDictComparerSection(
    ("is_pushable", bool, None),
    ("is_pushable_by_piston", bool, None),
))

raid_trigger_comparer =\
("minecraft:raid_trigger", dict, Comparer.UnnamedDictComparerSection(
    ("triggered_event", dict, EntitiesComparerTemplates.event_target_comparer),
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

reflect_projectiles_comparer =\
("minecraft:reflect_projectiles", dict, Comparer.UnnamedDictComparerSection(
    ("azimuth_angle", str, None),
    ("reflected_projectiles", list, Comparer.ListComparerSection(
        name="projectile",
        measure_length=True,
        ordered=False,
        types=(str,),
        comparer=None,
    )),
    ("reflection_scale", str, None),
))

rideable_comparer =\
("minecraft:rideable", dict, Comparer.UnnamedDictComparerSection(
    ("crouching_skip_interact", bool, None),
    ("family_types", list, EntitiesComparerTemplates.family_list_comparer),
    ("interact_text", str, None),
    ("passenger_max_width", decimal, None),
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
    ("end_scale", decimal, None),
    ("start_scale", decimal, None),
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
            ("admire", bool, None),
            ("barter", bool, None),
            ("consume_item", bool, None),
            ("craft_into", str, None),
            ("item", str, None),
            ("max_amount", int, None),
            ("pickup_limit", int, None),
            ("pickup_only", bool, None),
            ("priority", int, None),
            ("stored_in_inventory", bool, None),
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
    ("scheduled_events", list, EntitiesComparerTemplates.event_target_filters_list_comparer)
))

shooter_comparer = \
("minecraft:shooter", dict, EntitiesComparerTemplates.shooter_comparer)

sittable_comparer =\
("minecraft:sittable", dict, EntitiesComparerTemplates.empty_dict_comparer)

skin_id_comparer =\
("minecraft:skin_id", dict, EntitiesComparerTemplates.value_comparer)

spawn_entity_comparer =\
("minecraft:spawn_entity", dict, [
    (lambda key, value: "entities" in value, Comparer.UnnamedDictComparerSection(
        ("entities", (dict, list), [
            (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.spawn_entity_comparer),
            (lambda key, value: isinstance(value, list), Comparer.ListComparerSection(
                name="entity",
                ordered=False,
                measure_length=True,
                types=(dict,),
                comparer=EntitiesComparerTemplates.spawn_entity_comparer
            )),
        ]),
    )),
    (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.spawn_entity_comparer),
])

spell_effects_comparer =\
("minecraft:spell_effects", dict, Comparer.UnnamedDictComparerSection(
    ("add_effects", list, Comparer.ListComparerSection(
        name="effect",
        ordered=False,
        measure_length=True,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("display_on_screen_animation", bool, None),
            ("duration", int, None),
            ("effect", str, None),
            ("visible", bool, None),
        )
    )),
    ("remove_effects", str, None),
))

strength_comparer =\
("minecraft:strength", dict, EntitiesComparerTemplates.value_max_comparer)

suspect_tracking_comparer =\
("minecraft:suspect_tracking", dict, EntitiesComparerTemplates.empty_dict_comparer)

tameable_comparer =\
("minecraft:tameable", dict, Comparer.UnnamedDictComparerSection(
    ("probability", decimal, None),
    ("tame_event", dict, EntitiesComparerTemplates.event_target_comparer),
    ("tame_items", (list, str), [
        (lambda key, value: isinstance(value, list), EntitiesComparerTemplates.item_list_comparer),
        (lambda key, value: isinstance(value, str), None),
    ]),
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
    ("inside_range", decimal, None),
    ("must_see", bool, None),
    ("on_inside_range", dict, EntitiesComparerTemplates.event_target_comparer),
    ("on_outside_range", dict, EntitiesComparerTemplates.event_target_comparer),
    ("on_vision_lost_inside_range", dict, EntitiesComparerTemplates.event_target_comparer),
    ("outside_range", decimal, None),
))

teleport_comparer =\
("minecraft:teleport", dict, Comparer.UnnamedDictComparerSection(
    ("light_teleport_chance", decimal, None),
    ("max_random_teleport_time", int, None),
    ("random_teleport_cube", list, EntitiesComparerTemplates.coordinate_comparer),
    ("random_teleports", bool, None),
    ("target_distance", int, None),
    ("target_teleport_chance", decimal, None),
))

tick_world_comparer =\
("minecraft:tick_world", dict, EntitiesComparerTemplates.empty_dict_comparer)

timer_comparer =\
("minecraft:timer", dict, Comparer.UnnamedDictComparerSection(
    ("looping", bool, None),
    ("random_time_choices", list, Comparer.ListComparerSection(
        name="choice",
        ordered=False,
        measure_length=True,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("value", int, None),
            ("weight", int, None),
        )
    )),
    ("randomInterval", bool, None),
    ("time", (decimal, list), [
        (lambda key, value: isinstance(value, decimal), None),
        (lambda key, value: isinstance(value, list), EntitiesComparerTemplates.range_comparer),
    ]),
    ("time_down_event", dict, EntitiesComparerTemplates.event_target_comparer),
))

trade_resupply_comparer =\
("minecraft:trade_resupply", dict, EntitiesComparerTemplates.empty_dict_comparer)

trade_table_comparer =\
("minecraft:trade_table", dict, Comparer.UnnamedDictComparerSection(
    ("convert_trades_economy", bool, None),
    ("display_name", str, None),
    ("table", str, None),
))

trade_with_player_comparer =\
("minecraft:behavior.trade_with_player", dict, Comparer.UnnamedDictComparerSection(
    ("filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("priority", int, None),
))

trail_comparer =\
("minecraft:trail", dict, Comparer.UnnamedDictComparerSection(
    ("block_type", str, None),
    ("spawn_filter", dict, EntitiesComparerTemplates.filter_comparer),
))

transformation_comparer =\
("minecraft:transformation", dict, Comparer.UnnamedDictComparerSection(
    ("begin_transform_sound", str, None),
    ("delay", (dict, decimal), [
        (lambda key, value: isinstance(value, dict), Comparer.UnnamedDictComparerSection(
            ("block_assist_chance", decimal, None),
            ("block_chance", decimal, None),
            ("block_radius", int, None),
            ("block_types", list, EntitiesComparerTemplates.block_list_comparer),
            ("range_max", int, None),
            ("range_min", int, None),
            ("value", int, None),
        )),
        (lambda key, value: isinstance(value, decimal), None),
    ]),
    ("drop_equipment", bool, None),
    ("drop_inventory", bool, None),
    ("into", str, None),
    ("keep_level", bool, None),
    ("preserve_equipment", bool, None),
    ("transformation_sound", str, None),
))

trust_comparer =\
("minecraft:trust", dict, EntitiesComparerTemplates.empty_dict_comparer)

trusting_comparer =\
("minecraft:trusting", dict, Comparer.UnnamedDictComparerSection(
    ("probability", decimal, None),
    ("trust_event", dict, EntitiesComparerTemplates.event_target_comparer),
    ("trust_items", list, EntitiesComparerTemplates.item_list_comparer),
))

type_family_comparer =\
("minecraft:type_family", dict, Comparer.UnnamedDictComparerSection(
    ("family", list, EntitiesComparerTemplates.family_list_comparer),
))

underwater_movement_comparer =\
("minecraft:underwater_movement", dict, EntitiesComparerTemplates.value_comparer)

water_movement_comparer =\
("minecraft:water_movement", dict, Comparer.UnnamedDictComparerSection(
    ("drag_factor", decimal, None),
))

variable_max_auto_step_comparer =\
("minecraft:variable_max_auto_step", dict, Comparer.UnnamedDictComparerSection(
    ("base_value", decimal, None),
    ("controlled_value", decimal, None),
    ("jump_prevented_value", decimal, None),
))

variant_comparer =\
("minecraft:variant", dict, EntitiesComparerTemplates.value_comparer)

vibration_damper_comparer =\
("minecraft:vibration_damper", dict, EntitiesComparerTemplates.empty_dict_comparer)

vibration_listener_comparer =\
("minecraft:vibration_listener", dict, EntitiesComparerTemplates.empty_dict_comparer)

components_comparer_types = [
    addrider_comparer,
    admire_item_comparer,
    ageable_comparer,
    ambient_sound_interval_comparer,
    anger_level_comparer,
    angry_comparer,
    annotation_break_door_comparer,
    annotation_open_door_comparer,
    area_attack_comparer,
    attack_comparer,
    attack_cooldown_comparer,
    attack_damage_comparer,
    balloon_comparer,
    balloonable_comparer,
    barter_comparer,
    block_climber_comparer,
    block_sensor_comparer,
    boostable_comparer,
    boss_comparer,
    break_blocks_comparer,
    breathable_comparer,
    breedable_comparer,
    bribeable_comparer,
    buoyant_comparer,
    burns_in_daylight_comparer,
    can_climb_comparer,
    can_fly_comparer,
    can_join_raid_comparer,
    can_power_jump_comparer,
    celebrate_hunt_comparer,
    color_comparer,
    color2_comparer,
    collision_box_comparer,
    combat_regeneration_comparer,
    conditional_bandwidth_optimization_comparer,
    custom_hit_test_comparer,
    damage_over_time_comparer,
    damage_sensor_comparer,
    dash_comparer,
    delayed_attack,
    despawn_comparer,
    drying_out_timer_comparer,
    dweller_comparer,
    eat_block_comparer,
    economy_trade_table_comparer,
    entity_sensor_comparer,
    environment_sensor_comparer,
    equip_item_comparer,
    equipment_comparer,
    eqiuppable_comparer,
    exhaustion_values_comparer,
    experience_reward,
    explode_comparer,
    fire_immune_comparer,
    flocking_comparer,
    flying_speed_comparer,
    follow_range_comparer,
    game_event_movement_tracking_comparer,
    genetics_comparer,
    giveable_comparer,
    group_size_comparer,
    grows_crop_comparer,
    healable_comparer,
    health_comparer,
    heartbeat_comparer,
    hide_comparer,
    home_comparer,
    horse_jump_strength_comparer,
    hurt_on_condition_comparer,
    input_ground_controlled_comparer,
    inside_block_notifier_comparer,
    insomnia_comparer,
    interact_comparer,
    inventory_comparer,
    is_baby_comparer,
    is_charged_comparer,
    is_chested_comparer,
    is_dyeable_comparer,
    is_hidden_when_invisible,
    is_ignited_comparer,
    is_illager_captain_comparer,
    is_pregnant_comparer,
    is_saddled_comparer,
    is_shaking_comparer,
    is_sheared_comparer,
    is_stackable_comparer,
    is_stunned_comparer,
    is_tamed_comparer,
    item_controllable_comparer,
    item_hopper_comparer,
    jump_dynamic_comparer,
    jump_static_comparer,
    knockback_resistance_comparer,
    lava_movement_comparer,
    leashable_comparer,
    lookat_comparer,
    loot_comparer,
    managed_wandering_trader_comparer,
    mark_variant_comparer,
    mob_effect_comparer,
    movement_comparer,
    movement_amphibious_comparer,
    movement_basic_comparer,
    movement_fly_comparer,
    movement_generic_comparer,
    movement_glide_comparer,
    movement_hover_comparer,
    movement_jump_comparer,
    movement_skip_comparer,
    movement_sway_comparer,
    movement_sound_distance_offset_comparer,
    nameable_comparer,
    navigation_comparer,
    npc_comparer,
    on_death_comparer,
    on_friendly_anger,
    on_hurt_comparer,
    on_hurt_by_player_comparer,
    on_start_landing_comparer,
    on_start_takeoff_comparer,
    on_target_acquired_comparer,
    on_target_escape_comparer,
    on_wake_with_owner_comparer,
    out_of_control_comparer,
    peek_comparer,
    persistent_comparer,
    physics_comparer,
    player_exhaustion_comparer,
    player_experience_comparer,
    player_level_comparer,
    player_saturation_comparer,
    preferred_path_comparer,
    projectile_comparer,
    pushable_comparer,
    raid_trigger_comparer,
    rail_movement_comparer,
    rail_sensor_comparer,
    reflect_projectiles_comparer,
    rideable_comparer,
    scale_comparer,
    scale_by_age_comparer,
    shareables_comparer,
    scheduler_comparer,
    shooter_comparer,
    sittable_comparer,
    skin_id_comparer,
    spawn_entity_comparer,
    spell_effects_comparer,
    strength_comparer,
    suspect_tracking_comparer,
    tameable_comparer,
    tamemount_comparer,
    target_nearby_sensor_comparer,
    teleport_comparer,
    tick_world_comparer,
    timer_comparer,
    trade_resupply_comparer,
    trade_table_comparer,
    trade_with_player_comparer,
    trail_comparer,
    transformation_comparer,
    trust_comparer,
    trusting_comparer,
    type_family_comparer,
    underwater_movement_comparer,
    water_movement_comparer,
    variable_max_auto_step_comparer,
    variant_comparer,
    vibration_damper_comparer,
    vibration_listener_comparer,
]

components_comparer_types.extend(EntitiesComparerBehaviors.comparers)

comparer = Comparer.UnnamedDictComparerSection(
    *components_comparer_types,
    name="component",
    measure_length=True
)
