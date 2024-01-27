import Comparison.Comparer as Comparer
import DataMiners.Entities.EntitiesComparerTemplates as EntitiesComparerTemplates

avoid_mob_type =\
("minecraft:behavior.avoid_mob_type", dict, Comparer.UnnamedDictComparerSection(
    ("entity_types", list, EntitiesComparerTemplates.entity_types_comparers),
    ("priority", int, None),
    ("probability_per_strength", float, None),
))

breed_comparer =\
("minecraft:behavior.breed", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", float, None),
))

celebrate_comparer =\
("minecraft:behavior.celebrate", dict, Comparer.UnnamedDictComparerSection(
    ("celebration_sound", str, None),
    ("duration", float, None),
    ("jump_interval", dict, EntitiesComparerTemplates.range_dict_comparer),
    ("on_celebration_end_event", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("sound_interval", dict, EntitiesComparerTemplates.range_dict_comparer),
))

defend_trusted_target_comparer =\
("minecraft:behavior.defend_trusted_target", dict, Comparer.UnnamedDictComparerSection(
    ("aggro_sound", str, None),
    ("must_see", bool, None),
    ("on_defend_start", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("sound_chance", float, None),
    ("within_radius", int, None),
))

defend_village_target_comparer =\
("minecraft:behavior.defend_village_target", dict, Comparer.UnnamedDictComparerSection(
    ("attack_chance", float, None),
    ("entity_types", dict, EntitiesComparerTemplates.entity_types_comparer),
    ("must_reach", bool, None),
    ("priority", int, None),
))

dragonchargeplayer_comparer =\
("minecraft:behavior.dragonchargeplayer", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

dragondeath_comparer =\
("minecraft:behavior.dragondeath", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

dragonflaming_comparer =\
("minecraft:behavior.dragonflaming", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

dragonholdingpattern_comparer =\
("minecraft:behavior.dragonholdingpattern", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

dragonlanding_comparer =\
("minecraft:behavior.dragonlanding", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

dragonscanning_comparer =\
("minecraft:behavior.dragonscanning", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

dragonstrafeplayer_comparer =\
("minecraft:behavior.dragonstrafeplayer", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

dragontakeoff_comparer =\
("minecraft:behavior.dragontakeoff", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

drop_item_for_comparer =\
("minecraft:behavior.drop_item_for", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown", float, None),
    ("drop_item_chance", float, None),
    ("entity_types", list, EntitiesComparerTemplates.entity_types_comparers),
    ("goal_radius", float, None),
    ("loot_table", str, None),
    ("max_head_look_at_height", float, None),
    ("minimum_teleport_distance", float, None),
    ("offering_distance", float, None),
    ("on_drop_attempt", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("search_count", int, None),
    ("search_height", int, None),
    ("search_range", int, None),
    ("seconds_before_pickup", float, None),
    ("speed_multiplier", float, None),
    ("target_range", list, EntitiesComparerTemplates.coordinate_comparer),
    ("teleport_offset", list, EntitiesComparerTemplates.coordinate_comparer),
    ("time_of_day_range", list, EntitiesComparerTemplates.range_comparer),
))

eat_carried_item_comparer =\
("minecraft:behavior.eat_carried_item", dict, Comparer.UnnamedDictComparerSection(
    ("delay_before_eating", int, None),
    ("priority", int, None),
))

enderman_leave_block_comparer =\
("minecraft:behavior.enderman_leave_block", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

enderman_take_block_comparer =\
("minecraft:behavior.enderman_take_block", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

equip_item_comparer =\
("minecraft:behavior.equip_item", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

find_cover_comparer =\
("minecraft:behavior.find_cover", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_time", float, None),
    ("priority", int, None),
    ("speed_multiplier", int, None),
))

find_mount_comparer =\
("minecraft:behavior.find_mount", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("within_radius", int, None),
))

find_underwater_treasure_comparer =\
("minecraft:behavior.find_underwater_treasure", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("search_range", int, None),
    ("speed_multiplier", float, None),
    ("stop_distance", int, None),
))

flee_sun_comparer =\
("minecraft:behavior.flee_sun", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", int, None),
))

float_comparer =\
("minecraft:behavior.float", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

float_wander_comparer =\
("minecraft:behavior.float_wander", dict, Comparer.UnnamedDictComparerSection(
    ("float_duration", list, EntitiesComparerTemplates.range_comparer),
    ("must_reach", bool, None),
    ("priority", int, None),
    ("random_reselect", bool, None),
    ("xz_dist", int, None),
    ("y_dist", int, None),
    ("y_offset", float, None),
))

follow_owner_comparer =\
("minecraft:behavior.follow_owner", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", float, None),
    ("start_distance", int, None),
    ("stop_distance", int, None),
))

follow_parent_comparer =\
("minecraft:behavior.follow_parent", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", float, None),
))

guardian_attack_comparer =\
("minecraft:behavior.guardian_attack", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

hurt_by_target_comparer =\
("minecraft:behavior.hurt_by_target", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("entity_types", dict, EntitiesComparerTemplates.entity_types_comparers),
))

leap_at_target_comparer =\
("minecraft:behavior.leap_at_target", dict, Comparer.UnnamedDictComparerSection(
    ("must_be_on_ground", bool, None),
    ("priority", int, None),
    ("target_dist", float, None),
    ("yd", float, None),
))

look_at_entity_comparer =\
("minecraft:behavior.look_at_entity", dict, Comparer.UnnamedDictComparerSection(
    ("angle_of_view_horizontal", int, None),
    ("angle_of_view_vertical", int, None),
    ("filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("look_distance", float, None),
    ("priority", int, None),
    ("probability", float, None),
))

look_at_player_comparar =\
("minecraft:behavior.look_at_player", dict, Comparer.UnnamedDictComparerSection(
    ("look_distance", (float, int), None),
    ("priority", int, None),
    ("probability", float, None),
    ("target_distance", float, None),
))

melee_attack_comparer =\
("minecraft:behavior.melee_attack", dict, Comparer.UnnamedDictComparerSection(
    ("max_dist", int, None),
    ("melee_fov", int, None),
    ("on_kill", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("random_stop_interval", float, None),
    ("reach_multiplier", float, None),
    ("speed_multiplier", float, None),
    ("track_target", bool, None),
))

melee_box_attack_comparer =\
("minecraft:behavior.melee_box_attack", dict, Comparer.UnnamedDictComparerSection(
    ("attack_once", bool, None),
    ("can_spread_on_fire", bool, None),
    ("cooldown_time", (float, int), None),
    ("melee_fov", int, None),
    ("on_attack", dict, EntitiesComparerTemplates.event_target_comparer),
    ("on_kill", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("random_stop_interval", int, None),
    ("require_complete_path", bool, None),
    ("speed_multiplier", (float, int), None),
    ("track_target", bool, None),
))

mount_pathing_comparer =\
("minecraft:behavior.mount_pathing", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", float, None),
    ("target_dist", (float, int), None),
    ("track_target", bool, None),
))

move_through_village_comparer =\
("minecraft:behavior.move_through_village", dict, Comparer.UnnamedDictComparerSection(
    ("only_at_night", bool, None),
    ("priority", int, None),
    ("speed_multiplier", float, None),
))

move_to_village_comparer =\
("minecraft:behavior.move_to_village", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", float, None),
))

move_to_water_comparer =\
("minecraft:behavior.move_to_water", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("search_height", int, None),
    ("search_range", int, None),
))

move_towards_dwelling_restriction_comparer =\
("minecraft:behavior.move_towards_dwelling_restriction", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", int, None),
))

move_towards_home_restriction_comparer =\
("minecraft:behavior.move_towards_home_restriction", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", float, None),
))

move_towards_target_comparer =\
("minecraft:behavior.move_towards_target", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", float, None),
    ("within_radius", int, None),
))

nap_comparer =\
("minecraft:behavior.nap", dict, Comparer.UnnamedDictComparerSection(
    ("can_nap_filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("cooldown_max", float, None),
    ("cooldown_min", float, None),
    ("mob_detect_dist", float, None),
    ("mob_detect_height", float, None),
    ("priority", int, None),
    ("wake_mob_exceptions", dict, EntitiesComparerTemplates.filter_comparer),
))

nearest_attackable_target_comparer =\
("minecraft:behavior.nearest_attackable_target", dict, Comparer.UnnamedDictComparerSection(
    ("attack_interval", int, None),
    ("attack_interval_min", float, None),
    ("entity_types", list, EntitiesComparerTemplates.entity_types_comparers),
    ("must_reach", bool, None),
    ("must_see", bool, None),
    ("must_see_forget_duration", float, None),
    ("persist_time", float, None),
    ("priority", int, None),
    ("reselect_targets", bool, None),
    ("within_radius", float, None),
))

nearest_prioritized_attackable_target_comparer =\
("minecraft:behavior.nearest_prioritized_attackable_target", dict, Comparer.UnnamedDictComparerSection(
    ("attack_interval", int, None),
    ("entity_types", list, EntitiesComparerTemplates.entity_types_comparers),
    ("priority", int, None),
    ("reselect_targets", bool, None),
    ("target_search_height", int, None),
))

ocelot_sit_on_block_comparer =\
("minecraft:behavior.ocelot_sit_on_block", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", float, None),
))

ocelotattack_comparer =\
("minecraft:behavior.ocelotattack", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_time", float, None),
    ("max_distance", float, None),
    ("max_sneak_range", float, None),
    ("max_sprint_range", float, None),
    ("priority", int, None),
    ("reach_multiplier", float, None),
    ("sneak_speed_multiplier", float, None),
    ("sprint_speed_multiplier", float, None),
    ("walk_speed_multiplier", float, None),
    ("x_max_rotation", float, None),
    ("y_max_head_rotation", float, None),
))

offer_flower_comparer =\
("minecraft:behavior.offer_flower", dict, Comparer.UnnamedDictComparerSection(
    ("filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("priority", int, None),
))

panic_comparer =\
("minecraft:behavior.panic", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", float, None),
))

pet_sleep_with_owner_comparer =\
("minecraft:behavior.pet_sleep_with_owner", dict, Comparer.UnnamedDictComparerSection(
    ("goal_radius", float, None),
    ("priority", int, None),
    ("search_height", int, None),
    ("search_radius", int, None),
    ("speed_multiplier", float, None),
))

pickup_items_comparer =\
("minecraft:behavior.pickup_items", dict, Comparer.UnnamedDictComparerSection(
    ("can_pickup_any_item", bool, None),
    ("excluded_items", list, EntitiesComparerTemplates.item_list_comparer),
    ("goal_radius", int, None),
    ("max_dist", int, None),
    ("pickup_based_on_chance", bool, None),
    ("priority", int, None),
    ("speed_multiplier", float, None),
))

player_ride_tamed_comparer =\
("minecraft:behavior.player_ride_tamed", dict, Comparer.UnnamedDictComparerSection())

raid_garden_comparer =\
("minecraft:behavior.raid_garden", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("blocks", list, Comparer.ListComparerSection(
        name="block",
        ordered=False,
        measure_length=True,
        types=(str,),
        comparer=None
    )),
    ("speed_multiplier", float, None),
    ("search_range", int, None),
    ("search_height", int, None),
    ("goal_radius", float, None),
    ("max_to_eat", int, None),
    ("initial_eat_delay", int, None),
))

random_breach_comparer =\
("minecraft:behavior.random_breach", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_time", float, None),
    ("interval", int, None),
    ("priority", int, None),
    ("xz_dist", int, None),
))

random_look_around_comparer =\
("minecraft:behavior.random_look_around", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

random_look_around_and_sit_comparer =\
("minecraft:behavior.random_look_around_and_sit", dict, Comparer.UnnamedDictComparerSection(
    ("max_look_count", int, None),
    ("max_look_time", int, None),
    ("min_look_count", int, None),
    ("min_look_time", int, None),
    ("priority", int, None),
    ("probability", float, None),
))

random_stroll_comparer =\
("minecraft:behavior.random_stroll", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", (float, int), None),
    ("xz_dist", int, None),
))

random_swim_comparer =\
("minecraft:behavior.random_swim", dict, Comparer.UnnamedDictComparerSection(
    ("avoid_surface", bool, None),
    ("interval", int, None),
    ("priority", int, None),
    ("speed_multiplier", float, None),
    ("xz_dist", int, None),
    ("y_dist", int, None),
))

ranged_attack_comparer =\
("minecraft:behavior.ranged_attack", dict, Comparer.UnnamedDictComparerSection(
    ("attack_interval_max", float, None),
    ("attack_interval_min", float, None),
    ("attack_radius", (float, int), None),
    ("burst_interval", float, None),
    ("burst_shots", int, None),
    ("charge_charged_trigger", (float, int), None),
    ("charge_shoot_trigger", (float, int), None),
    ("priority", int, None),
    ("swing", bool, None),
))

run_around_like_crazy_comparer =\
("minecraft:behavior.run_around_like_crazy", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", float, None),
))

send_event_comparer =\
("minecraft:behavior.send_event", dict, Comparer.UnnamedDictComparerSection(
    ("event_choices", list, EntitiesComparerTemplates.choice_comparer),
    ("priority", int, None),
))

stalk_and_pounce_on_target_comparer =\
("minecraft:behavior.stalk_and_pounce_on_target", dict, Comparer.UnnamedDictComparerSection(
    ("interest_time", float, None),
    ("leap_dist", float, None),
    ("leap_height", float, None),
    ("max_stalk_dist", float, None),
    ("pounce_max_dist", float, None),
    ("priority", int, None),
    ("stalk_speed", float, None),
    ("strike_dist", float, None),
    ("stuck_blocks", dict, EntitiesComparerTemplates.filter_comparer),
    ("stuck_time", float, None),
))

stay_while_sitting_comparer =\
("minecraft:behavior.stay_while_sitting", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

stomp_turtle_egg_comparer =\
("minecraft:behavior.stomp_turtle_egg", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", int, None),
    ("search_range", int, None),
    ("search_height", int, None),
    ("goal_radius", float, None),
    ("interval", int, None),
))

stroll_towards_village_comparer =\
("minecraft:behavior.stroll_towards_village", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_time", float, None),
    ("goal_radius", float, None),
    ("priority", int, None),
    ("search_range", int, None),
    ("speed_multiplier", float, None),
    ("start_chance", float, None),
))

summon_entity_comparer =\
("minecraft:behavior.summon_entity", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("summon_choices", list, EntitiesComparerTemplates.choice_comparer),
))

swell_comparer =\
("minecraft:behavior.swell", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("start_distance", float, None),
    ("stop_distance", float, None),
))

swim_idle_comparer =\
("minecraft:behavior.swim_idle", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("idle_time", float, None),
    ("success_rate", float, None),
))

swim_wander_comparer =\
("minecraft:behavior.swim_wander", dict, Comparer.UnnamedDictComparerSection(
    ("interval", float, None),
    ("look_ahead", float, None),
    ("priority", int, None),
    ("speed_multiplier", float, None),
    ("wander_time", float, None),
))

swim_with_entity_comparer =\
("minecraft:behavior.swim_with_entity", dict, Comparer.UnnamedDictComparerSection(
    ("catch_up_multiplier", float, None),
    ("catch_up_threshold", float, None),
    ("chance_to_stop", float, None),
    ("entity_types", list, EntitiesComparerTemplates.entity_types_comparers),
    ("match_direction_threshold", float, None),
    ("priority", int, None),
    ("search_range", float, None),
    ("speed_multiplier", float, None),
    ("state_check_interval", float, None),
    ("stop_distance", float, None),
    ("success_rate", float, None),
))

target_when_pushed_comparer =\
("minecraft:behavior.target_when_pushed", dict, Comparer.UnnamedDictComparerSection(
    ("entity_types", (dict, list), EntitiesComparerTemplates.entity_types_comparers),
    ("percent_chance", float, None),
    ("priority", int, None),
))

tempt_comparer =\
("minecraft:behavior.tempt", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", float, None),
    ("within_radius", int, None),
    ("can_get_scared", bool, None),
    ("tempt_sound", str, None),
    ("sound_interval", list, EntitiesComparerTemplates.range_comparer),
    ("items", list, EntitiesComparerTemplates.item_list_comparer),
))

comparers = [
    avoid_mob_type,
    breed_comparer,
    celebrate_comparer,
    defend_trusted_target_comparer,
    defend_village_target_comparer,
    dragonchargeplayer_comparer,
    dragondeath_comparer,
    dragonflaming_comparer,
    dragonholdingpattern_comparer,
    dragonlanding_comparer,
    dragonscanning_comparer,
    dragonstrafeplayer_comparer,
    dragontakeoff_comparer,
    drop_item_for_comparer,
    eat_carried_item_comparer,
    enderman_leave_block_comparer,
    enderman_take_block_comparer,
    equip_item_comparer,
    find_cover_comparer,
    find_mount_comparer,
    find_underwater_treasure_comparer,
    flee_sun_comparer,
    float_comparer,
    float_wander_comparer,
    follow_owner_comparer,
    follow_parent_comparer,
    guardian_attack_comparer,
    hurt_by_target_comparer,
    leap_at_target_comparer,
    look_at_entity_comparer,
    look_at_player_comparar,
    melee_attack_comparer,
    melee_box_attack_comparer,
    mount_pathing_comparer,
    move_to_village_comparer,
    move_to_water_comparer,
    move_through_village_comparer,
    move_towards_dwelling_restriction_comparer,
    move_towards_home_restriction_comparer,
    move_towards_target_comparer,
    nap_comparer,
    nearest_attackable_target_comparer,
    nearest_prioritized_attackable_target_comparer,
    ocelot_sit_on_block_comparer,
    ocelotattack_comparer,
    offer_flower_comparer,
    panic_comparer,
    pet_sleep_with_owner_comparer,
    pickup_items_comparer,
    player_ride_tamed_comparer,
    raid_garden_comparer,
    random_breach_comparer,
    random_look_around_comparer,
    random_look_around_and_sit_comparer,
    random_stroll_comparer,
    random_swim_comparer,
    ranged_attack_comparer,
    run_around_like_crazy_comparer,
    send_event_comparer,
    stalk_and_pounce_on_target_comparer,
    stay_while_sitting_comparer,
    stomp_turtle_egg_comparer,
    stroll_towards_village_comparer,
    summon_entity_comparer,
    swell_comparer,
    swim_idle_comparer,
    swim_wander_comparer,
    swim_with_entity_comparer,
    target_when_pushed_comparer,
    tempt_comparer,
]
