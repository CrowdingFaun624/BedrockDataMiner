from typing import Any, TYPE_CHECKING

import Comparison.Comparer as Comparer
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks

import DataMiners.Entities.EntitiesComparerBehaviors as EntitiesComparerBehaviors
import DataMiners.Entities.EntitiesComparerTemplates as EntitiesComparerTemplates

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.Entities, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.Entities:
    behavior_packs:DataMinerTyping.BehaviorPacks = dataminers["behavior_packs"].get_data_file(version, non_exist_ok=True)
    if behavior_packs is None:
        behavior_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}]
    def fix_weird_components(entity_behavior_packs:dict[str,Any]) -> dict[str,Any]:
        # deletes components that are, for some reason, outside of the "components" or "component_groups" keys
        for behavior_pack_name, entity_data in entity_behavior_packs.items():
            for key_to_delete in [key for key in entity_data["minecraft:entity"] if key.startswith("minecraft:")]:
                del entity_data["minecraft:entity"][key_to_delete]
        return entity_behavior_packs
    return {entity_name: fix_weird_components(CollapseResourcePacks.collapse_resource_packs(entity_behavior_packs, behavior_packs, version.name)) for entity_name, entity_behavior_packs in data.items()}

def behavior_pack_comparison_move_function(key:str, value:DataMinerTyping.NormalizedBlocksJsonBlockTypedDict) -> DataMinerTyping.NormalizedBlocksJsonBlockTypedDict:
    output = value.copy()
    del output["defined_in"]
    return output

components_comparer_types = [
    ("minecraft:addrider", dict, Comparer.UnnamedDictComparerSection(
        ("entity_type", str, None),
    )),
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
    )),
    ("minecraft:ambient_sound_interval", dict, Comparer.UnnamedDictComparerSection(
        ("value", (float, int), None),
        ("range", (float, int), None),
        ("event_name", str, None),
    )),
    ("minecraft:angry", dict, Comparer.UnnamedDictComparerSection(
        ("broadcast_anger", bool, None),
        ("broadcast_range", int, None),
        ("duration", int, None),
        ("duration_delta", int, None),
        ("calm_event", dict, EntitiesComparerTemplates.event_target_comparer),
    )),
    (EntitiesComparerTemplates.get_component_key("minecraft:annotation", ["break_door"]), dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:attack", dict, Comparer.UnnamedDictComparerSection(
        *EntitiesComparerTemplates.damage_comparer
    )),
    ("minecraft:attack_damage", dict, EntitiesComparerTemplates.value_max_comparer),
    ("minecraft:balloon", dict, Comparer.UnnamedDictComparerSection(
        ("lift_force", list, EntitiesComparerTemplates.coordinate_comparer),
    )),
    ("minecraft:balloonable", dict, Comparer.UnnamedDictComparerSection(
        ("mass", float, None),
    )),
    # (EntitiesComparerTemplates.get_component_key("minecraft:behavior", [
    #     "avoid_mob_type", "breed", "celebrate", "dragonchargeplayer",
    #     "dragondeath", "dragonflaming",
    #     "dragonholdingpattern", "dragonlanding", "dragonscanning", "dragonstrafeplayer",
    #     "dragontakeoff", "drop_item_for", "enderman_leave_block", "enderman_take_block",
    #     "equip_item", "find_underwater_treasure", "flee_sun", "float",
    #     "float_wander", "follow_owner", "follow_parent", "guardian_attack",
    #     "hurt_by_target", "leap_at_target", "look_at_entity", "look_at_player",
    #     "melee_attack", "melee_box_attack", "mount_pathing", "move_to_village",
    #     "move_to_water",
    #     "move_towards_dwelling_restriction", "move_towards_home_restriction", "move_towards_restriction", "nearest_attackable_target",
    #     "ocelot_sit_on_block", "ocelotattack", "panic", "pet_sleep_with_owner",
    #     "pickup_items", "player_ride_tamed", "random_breach", "random_look_around",
    #     "random_stroll", "random_swim", "ranged_attack", "run_around_like_crazy",
    #     "stay_while_sitting", "stomp_turtle_egg", "swell", "swim_idle",
    #     "swim_wander", "swim_with_entity", "tempt",
    #     ]), dict, Comparer.UnnamedDictComparerSection(
    #         ("angle_of_view_horizontal", int, None),
    #         ("angle_of_view_vertical", int, None),
    #         ("attack_interval", (float, int), None),
    #         ("attack_interval_max", (float, int), None),
    #         ("attack_interval_min", (float, int), None),
    #         ("attack_radius", (float, int), None),
    #         ("avoid_surface", bool, None),
    #         ("burst_interval", float, None),
    #         ("burst_shots", int, None),
    #         ("can_get_scared", bool, None),
    #         ("can_pickup_any_item", bool, None),
    #         ("can_spread_on_fire", bool, None),
    #         ("catch_up_multiplier", float, None),
    #         ("catch_up_threshold", float, None),
    #         ("celebration_sound", str, None),
    #         ("chance_to_stop", float, None),
    #         ("charge_charged_trigger", float, None),
    #         ("charge_shoot_trigger", float, None),
    #         ("cooldown", float, None),
    #         ("cooldown_time", float, None),
    #         ("drop_item_chance", float, None),
    #         ("duration", float, None),
    #         ("entity_types", (dict, list), EntityComparerTemplates.entity_types_comparers),
    #         ("excluded_items", list, EntitiesComparerTemplates.item_list_comparer),
    #         ("filters", dict, [
    #             (lambda key, value: "value" in value, EntitiesComparerTemplates.filter_comparer),
    #             (lambda key, value: True, EntitiesComparerTemplates.many_filters_comparer),
    #         ]),
    #         ("float_duration", list, EntitiesComparerTemplates.range_comparer),
    #         ("goal_radius", (float, int), None),
    #         ("idle_time", float, None),
    #         ("interval", (float, int), None),
    #         ("items", list, EntitiesComparerTemplates.item_list_comparer),
    #         ("jump_interval", dict, EntitiesComparerTemplates.range_dict_comparer),
    #         ("look_ahead", float, None),
    #         ("look_distance", (float, int), None),
    #         ("loot_table", str, None),
    #         ("match_direction_threshold", float, None),
    #         ("max_dist", int, None),
    #         ("max_distance", float, None),
    #         ("max_head_look_at_height", float, None),
    #         ("max_sneak_range", float, None),
    #         ("max_sprint_range", float, None),
    #         ("minimum_teleport_distance", float, None),
    #         ("must_be_on_ground", bool, None),
    #         ("must_see", bool, None),
    #         ("must_see_forget_duration", float, None),
    #         ("offering_distance", (float, int), None),
    #         ("on_celebration_end_event", dict, EntitiesComparerTemplates.event_target_comparer),
    #         ("on_drop_attempt", dict, EntitiesComparerTemplates.event_target_comparer),
    #         ("persist_time", float, None),
    #         ("pickup_based_on_chance", bool, None),
    #         ("priority", int, None),
    #         ("probability", float, None),
    #         ("probability_per_strength", float, None),
    #         ("random_reselect", bool, None),
    #         ("random_stop_interval", (float, int), None),
    #         ("reach_multiplier", float, None),
    #         ("require_complete_path", bool, None),
    #         ("reselect_targets", bool, None),
    #         ("search_count", int, None),
    #         ("search_height", int, None),
    #         ("search_radius", int, None),
    #         ("search_range", (float, int), None),
    #         ("seconds_before_pickup", float, None),
    #         ("sneak_speed_multiplier", float, None),
    #         ("sound_interval", (dict, list), [
    #             (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.range_dict_comparer),
    #             (lambda key, value: isinstance(value, list), EntitiesComparerTemplates.range_comparer),
    #         ]),
    #         ("speed_multiplier", (float, int), None),
    #         ("sprint_speed_multiplier", float, None),
    #         ("start_distance", (float, int), None),
    #         ("state_check_interval", float, None),
    #         ("stop_distance", (float, int), None),
    #         ("success_rate", float, None),
    #         ("swing", bool, None),
    #         ("target_dist", (float, int), None),
    #         ("target_range", list, EntitiesComparerTemplates.coordinate_comparer),
    #         ("teleport_offset", list, EntitiesComparerTemplates.coordinate_comparer),
    #         ("tempt_sound", str, None),
    #         ("time_of_day_range", list, EntitiesComparerTemplates.range_comparer),
    #         ("track_target", bool, None),
    #         ("walk_speed_multiplier", float, None),
    #         ("wander_time", float, None),
    #         ("within_radius", (float, int), None),
    #         ("x_max_rotation", float, None),
    #         ("xz_dist", int, None),
    #         ("y_dist", int, None),
    #         ("y_max_head_rotation", float, None),
    #         ("y_offset", float, None),
    #         ("yd", float, None),
    #     )
    # ),
    ("minecraft:block_climber", dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:boss", dict, Comparer.UnnamedDictComparerSection(
        ("should_darken_sky", bool, None),
        ("hud_range", int, None),
    )),
    ("minecraft:breathable", dict, Comparer.UnnamedDictComparerSection(
        ("breathes_air", bool, None),
        ("breathes_water", bool, None),
        ("generates_bubbles", bool, None),
        ("suffocate_time", int, None),
        ("suffocateTime", int, None),
        ("total_supply", int, None),
        ("totalSupply", int, None),
    )),
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
        ("parent_centric_attribute_blending", list, Comparer.ListComparerSection(
            name="attribute",
            measure_length=True,
            types=(str,),
            print_all=True,
            comparer=None,
        )),
        ("require_full_health", bool, None),
        ("require_tame", bool, None),
    )),
    ("minecraft:bribeable", dict, Comparer.UnnamedDictComparerSection(
        ("bribe_items", list, EntitiesComparerTemplates.item_list_comparer),
    )),
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
    )),
    ("minecraft:burns_in_daylight", dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:can_climb", dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:can_fly", dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:can_join_raid", dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:can_power_jump", dict, EntitiesComparerTemplates.empty_dict_comparer), 
    ("minecraft:color", dict, EntitiesComparerTemplates.value_max_comparer),
    ("minecraft:collision_box", dict, Comparer.UnnamedDictComparerSection(
        ("height", (float, int), None),
        ("width", (float, int), None),
    )),
    ("minecraft:conditional_bandwidth_optimization", dict, Comparer.UnnamedDictComparerSection(
        ("conditional_values", list, Comparer.ListComparerSection(
            name="conditional value",
            types=(dict,),
            ordered=False,
            measure_length=True,
            comparer=EntitiesComparerTemplates.conditional_bandwidth_optimization_values_comparer
        )),
        ("default_values", dict, EntitiesComparerTemplates.conditional_bandwidth_optimization_values_comparer),
    )),
    ("minecraft:damage_over_time", dict, Comparer.UnnamedDictComparerSection(
        ("damage_per_hurt", int, None),
        ("time_between_hurt", int, None),
    )),
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
    )),
    ("minecraft:despawn", dict, Comparer.UnnamedDictComparerSection(
        ("despawn_from_distance", dict, Comparer.UnnamedDictComparerSection(
            ("min_distance", int, None),
            ("max_distance", int, None),
        )),
    )),
    ("minecraft:drying_out_timer", dict, Comparer.UnnamedDictComparerSection(
        ("dried_out_event", dict, EntitiesComparerTemplates.event_target_comparer),
        ("recover_after_dried_out_event", dict, EntitiesComparerTemplates.event_target_comparer),
        ("stopped_drying_out_event", dict, EntitiesComparerTemplates.event_target_comparer),
        ("total_time", int, None),
        ("water_bottle_refill_time", int, None),
    )),
    ("minecraft:dweller", dict, Comparer.UnnamedDictComparerSection(
        ("can_find_poi", bool, None),
        ("can_migrate", bool, None),
        ("dweller_role", str, None),
        ("dwelling_type", str, None),
        ("first_founding_reward", int, None),
        ("update_interval_base", int, None),
        ("update_interval_variant", int, None),
    )),
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
    )),
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
    )),
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
    )),
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
    )),
    ("minecraft:experience_reward", dict, Comparer.UnnamedDictComparerSection(
        ("on_bred", str, None),
        ("on_death", str, None),
    )),
    ("minecraft:explode", dict, Comparer.UnnamedDictComparerSection(
        ("causes_fire", bool, None),
        ("destroy_affected_by_griefing", bool, None),
        ("fire_affected_by_griefing", bool, None),
        ("fuse_length", (float, int), None),
        ("fuse_lit", bool, None),
        ("power", int, None),
    )),
    ("minecraft:fire_immune", (bool, dict), [
        (lambda key, value: isinstance(value, bool), None),
        (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.empty_dict_comparer),
    ]),
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
    )),
    ("minecraft:flying_speed", dict, EntitiesComparerTemplates.value_max_comparer),
    ("minecraft:follow_range", dict, EntitiesComparerTemplates.value_max_comparer),
    ("minecraft:game_event_movement_tracking", dict, Comparer.UnnamedDictComparerSection(
        ("emit_flap", bool, None),
    )),
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
    )),
    ("minecraft:health", dict, Comparer.UnnamedDictComparerSection(
        ("max", int, None),
        ("value", (dict, int), [
            (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.range_dict_comparer),
            (lambda key, value: isinstance(value, int), None),
        ]),
    )),
    ("minecraft:home", dict, Comparer.UnnamedDictComparerSection(
        ("restriction_radius", int, None),
    )),
    (EntitiesComparerTemplates.get_component_key("minecraft:horse", ["jump_strength"]), dict, EntitiesComparerTemplates.value_max_comparer),
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
    )),
    ("minecraft:input_ground_controlled", dict, EntitiesComparerTemplates.empty_dict_comparer),
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
    )),
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
    )),
    ("minecraft:inventory", dict, Comparer.UnnamedDictComparerSection(
        ("inventory_size", int, None),
        ("can_be_siphoned_from", bool, None),
        ("container_type", str, None),
        ("restrict_to_owner", bool, None),
    )),
    ("minecraft:is_baby", dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:is_charged", dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:is_chested", dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:is_dyeable", dict, Comparer.UnnamedDictComparerSection(
        ("interact_text", str, None),
    )),
    ("minecraft:is_hidden_when_invisible", dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:is_saddled", dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:is_stackable", dict, EntitiesComparerTemplates.value_max_comparer),
    ("minecraft:is_tamed", dict, EntitiesComparerTemplates.empty_dict_comparer),
    (EntitiesComparerTemplates.get_component_key("minecraft:jump", ["static"]), dict, Comparer.UnnamedDictComparerSection(
        ("jump_power", float, None),
    )),
    ("minecraft:knockback_resistance", dict, EntitiesComparerTemplates.value_max_comparer),
    ("minecraft:leashable", dict, Comparer.UnnamedDictComparerSection(
        ("soft_distance", float, None),
        ("hard_distance", float, None),
        ("max_distance", float, None),
    )),
    ("minecraft:lookat", dict, Comparer.UnnamedDictComparerSection(
        ("search_radius", float, None),
        ("set_target", bool, None),
        ("look_cooldown", float, None),
        ("filters", dict, EntitiesComparerTemplates.filter_comparer),
    )),
    ("minecraft:loot", dict, Comparer.UnnamedDictComparerSection(
        ("table", str, None),
    )),
    (EntitiesComparerTemplates.get_component_key("minecraft:movement", ["basic", "generic", "sway"]), dict, Comparer.UnnamedDictComparerSection(
        ("sway_amplitude", float, None),
        ("max", (float, int), None),
        ("value", (float, int), None),
    )),
    ("minecraft:nameable", dict, Comparer.UnnamedDictComparerSection(
        ("always_show", bool, None),
        ("allow_name_tag_renaming", bool, None),
    )),
    (EntitiesComparerTemplates.get_component_key("minecraft:navigation", ["climb", "float", "generic", "walk"]), dict, Comparer.UnnamedDictComparerSection(
        ("avoid_damage_blocks", bool, None),
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
    )),
    ("minecraft:on_death", dict, EntitiesComparerTemplates.event_target_comparer),
    ("minecraft:on_hurt", dict, EntitiesComparerTemplates.event_target_comparer),
    ("minecraft:on_hurt_by_player", dict, EntitiesComparerTemplates.event_target_comparer),
    ("minecraft:on_start_landing", dict, EntitiesComparerTemplates.event_target_comparer),
    ("minecraft:on_start_takeoff", dict, EntitiesComparerTemplates.event_target_comparer),
    ("minecraft:on_target_acquired", dict, EntitiesComparerTemplates.event_target_comparer),
    ("minecraft:on_target_escape", dict, EntitiesComparerTemplates.event_target_comparer),
    ("minecraft:on_wake_with_owner", dict, EntitiesComparerTemplates.event_target_comparer),
    ("minecraft:out_of_control", dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:persistent", dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:physics", dict, Comparer.UnnamedDictComparerSection(
        ("has_collision", bool, None),
        ("has_gravity", bool, None),
    )),
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
                ("radius_on_use", int, None),
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
    )),
    ("minecraft:pushable", dict, Comparer.UnnamedDictComparerSection(
        ("is_pushable", bool, None),
        ("is_pushable_by_piston", bool, None),
    )),
    ("minecraft:rail_movement", dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:rail_sensor", dict, Comparer.UnnamedDictComparerSection(
        ("check_block_types", bool, None),
        ("eject_on_activate", bool, None),
        ("eject_on_deactivate", bool, None),
        ("tick_command_block_on_activate", bool, None),
        ("tick_command_block_on_deactivate", bool, None),
        ("on_activate", dict, EntitiesComparerTemplates.event_target_filters_comparer),
        ("on_deactivate", dict, EntitiesComparerTemplates.event_target_filters_comparer),
    )),
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
    )),
    ("minecraft:scale", (bool, dict), EntitiesComparerTemplates.value_max_comparer),
    ("minecraft:scale_by_age", dict, Comparer.UnnamedDictComparerSection(
        ("end_scale", float, None),
        ("start_scale", float, None),
    )),
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
    )),
    ("minecraft:shooter", dict, Comparer.UnnamedDictComparerSection(
        ("sound", str, None),
        ("type", str, None),
        ("def", str, None),
    )),
    ("minecraft:sittable", dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:spawn_entity", dict, [
        (lambda key, value: "entities" in value, Comparer.UnnamedDictComparerSection(
            ("entities", dict, EntitiesComparerTemplates.spawn_entity_comparer),
        )),
        (lambda key, value: True, EntitiesComparerTemplates.spawn_entity_comparer),
    ]),
    ("minecraft:tameable", dict, Comparer.UnnamedDictComparerSection(
        ("probability", float, None),
        ("tame_event", dict, EntitiesComparerTemplates.event_target_comparer),
        ("tame_items", list, EntitiesComparerTemplates.item_list_comparer),
    )),
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
    )),
    ("minecraft:target_nearby_sensor", dict, Comparer.UnnamedDictComparerSection(
        ("inside_range", float, None),
        ("must_see", bool, None),
        ("on_inside_range", dict, EntitiesComparerTemplates.event_target_comparer),
        ("on_outside_range", dict, EntitiesComparerTemplates.event_target_comparer),
        ("on_vision_lost_inside_range", dict, EntitiesComparerTemplates.event_target_comparer),
        ("outside_range", float, None),
    )),
    ("minecraft:teleport", dict, Comparer.UnnamedDictComparerSection(
        ("light_teleport_chance", float, None),
        ("max_random_teleport_time", int, None),
        ("random_teleport_cube", list, EntitiesComparerTemplates.coordinate_comparer),
        ("random_teleports", bool, None),
        ("target_distance", int, None),
        ("target_teleport_chance", float, None),
    )),
    ("minecraft:tick_world", dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:timer", dict, Comparer.UnnamedDictComparerSection(
        ("looping", bool, None),
        ("time", int, None),
        ("time_down_event", dict, EntitiesComparerTemplates.event_target_comparer),
    )),
    ("minecraft:trust", dict, EntitiesComparerTemplates.empty_dict_comparer),
    ("minecraft:type_family", dict, Comparer.UnnamedDictComparerSection(
        ("family", list, EntitiesComparerTemplates.family_list_comparer),
    )),
    ("minecraft:underwater_movement", dict, EntitiesComparerTemplates.value_max_comparer),
    ("minecraft:variable_max_auto_step", dict, Comparer.UnnamedDictComparerSection(
        ("base_value", float, None),
        ("jump_prevented_value", float, None),
    )),
    ("minecraft:variant", dict, EntitiesComparerTemplates.value_max_comparer),
]
components_comparer_types.extend(EntitiesComparerBehaviors.comparers)

components_comparer = Comparer.UnnamedDictComparerSection(
    *components_comparer_types
)


comparer = Comparer.Comparer(
    normalizer=normalize,
    dependencies=["behavior_packs"],
    base_comparer_section=Comparer.DictComparerSection(
        name="entity",
        key_types=(str,),
        value_types=(dict,),
        detect_key_moves=False, # haha lol no not doing that right now
        measure_length=True,
        comparer=Comparer.DictComparerSection(
            name="behavior pack",
            key_types=(str,),
            value_types=(dict,),
            measure_length=True,
            detect_key_moves=True,
            comparison_move_function=behavior_pack_comparison_move_function,
            comparer=Comparer.UnnamedDictComparerSection(
                ("defined_in", list, Comparer.ListComparerSection(
                    name="behavior pack",
                    types=(str,),
                    ordered=False,
                    measure_length=True,
                    comparer=None,
                )),
                ("format_version", str, None),
                ("minecraft:entity", dict, Comparer.UnnamedDictComparerSection(
                    ("description", dict, Comparer.UnnamedDictComparerSection(
                        ("identifier", str, None),
                        ("is_spawnable", bool, None),
                        ("is_summonable", bool, None),
                        ("is_experimental", bool, None),
                        name="description"
                    )),
                    ("component_groups", dict, Comparer.DictComparerSection(
                        name="component group",
                        key_types=(str,),
                        value_types=(dict,),
                        measure_length=True,
                        comparer=components_comparer
                    )),
                    ("components", dict, components_comparer),
                    ("events", dict, EntitiesComparerTemplates.events_comparer),
                ))
            )
        )
    )
)
