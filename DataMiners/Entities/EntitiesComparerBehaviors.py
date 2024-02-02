import Comparison.Comparer as Comparer
import DataMiners.Entities.EntitiesComparerTemplates as EntitiesComparerTemplates

decimal = float|int

admire_item_comparer =\
("minecraft:behavior.admire_item", dict, Comparer.UnnamedDictComparerSection(
    ("admire_item_sound", str, None),
    ("on_admire_item_start", dict, EntitiesComparerTemplates.event_target_comparer),
    ("on_admire_item_stop", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("sound_interval", dict, EntitiesComparerTemplates.range_dict_comparer),
))

avoid_block_comparer =\
("minecraft:behavior.avoid_block", dict, Comparer.UnnamedDictComparerSection(
    ("avoid_block_sound", str, None),
    ("on_escape", list, EntitiesComparerTemplates.event_target_list_comparer),
    ("priority", int, None),
    ("search_height", int, None),
    ("search_range", int, None),
    ("sprint_speed_modifier", decimal, None),
    ("sound_interval", dict, EntitiesComparerTemplates.range_dict_comparer),
    ("target_blocks", list, EntitiesComparerTemplates.block_list_comparer),
    ("target_selection_method", str, None),
    ("tick_interval", int, None),
    ("walk_speed_modifier", decimal, None),
))

avoid_mob_type_comparer =\
("minecraft:behavior.avoid_mob_type", dict, Comparer.UnnamedDictComparerSection(
    ("avoid_mob_sound", str, None),
    ("entity_types", list, EntitiesComparerTemplates.entity_types_comparers),
    ("ignore_visibility", bool, None),
    ("max_dist", decimal, None),
    ("max_flee", int, None),
    ("on_escape_event", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("probability_per_strength", decimal, None),
    ("remove_target", bool, None),
    ("sound_interval", dict, EntitiesComparerTemplates.range_dict_comparer),
))

barter_comparer =\
("minecraft:behavior.barter", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

beg_comparer =\
("minecraft:behavior.beg", dict, Comparer.UnnamedDictComparerSection(
    ("items", list, EntitiesComparerTemplates.item_list_comparer),
    ("look_distance", decimal, None),
    ("look_time", list, EntitiesComparerTemplates.range_comparer),
    ("priority", int, None),
))

breed_comparer =\
("minecraft:behavior.breed", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

celebrate_comparer =\
("minecraft:behavior.celebrate", dict, Comparer.UnnamedDictComparerSection(
    ("celebration_sound", str, None),
    ("duration", decimal, None),
    ("jump_interval", dict, EntitiesComparerTemplates.range_dict_comparer),
    ("on_celebration_end_event", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("sound_interval", dict, EntitiesComparerTemplates.range_dict_comparer),
))

celebrate_survive_comparer =\
("minecraft:behavior.celebrate_survive", dict, Comparer.UnnamedDictComparerSection(
    ("duration", float, None),
    ("fireworks_interval", dict, EntitiesComparerTemplates.range_dict_comparer),
    ("on_celebration_end_event", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
))

charge_attack_comparer =\
("minecraft:behavior.charge_attack", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

charge_held_item_comparer =\
("minecraft:behavior.charge_held_item", dict, Comparer.UnnamedDictComparerSection(
    ("items", list, EntitiesComparerTemplates.item_list_comparer),
    ("priority", int, None),
))

circle_around_anchor_comparer =\
("minecraft:behavior.circle_around_anchor", dict, Comparer.UnnamedDictComparerSection(
    ("angle_change", decimal, None),
    ("goal_radius", decimal, None),
    ("height_above_target_range", list, EntitiesComparerTemplates.range_comparer),
    ("height_adjustment_chance", decimal, None),
    ("height_offset_range", list, EntitiesComparerTemplates.range_comparer),
    ("priority", int, None),
    ("radius_adjustment_chance", decimal, None),
    ("radius_change", decimal, None),
    ("radius_range", list, EntitiesComparerTemplates.range_comparer),
))

controlled_by_player_comparer =\
("minecraft:behavior.controlled_by_player", dict, Comparer.UnnamedDictComparerSection(
    ("mount_speed_multiplier", decimal, None),
    ("priority", int, None),
))

croak_comparer =\
("minecraft:behavior.croak", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("interval", list, EntitiesComparerTemplates.range_comparer),
    ("duration", decimal, None),
    ("filters", dict, EntitiesComparerTemplates.filter_comparer)
))

defend_trusted_target_comparer =\
("minecraft:behavior.defend_trusted_target", dict, Comparer.UnnamedDictComparerSection(
    ("aggro_sound", str, None),
    ("must_see", bool, None),
    ("on_defend_start", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("sound_chance", decimal, None),
    ("within_radius", int, None),
))

defend_village_target_comparer =\
("minecraft:behavior.defend_village_target", dict, Comparer.UnnamedDictComparerSection(
    ("attack_chance", decimal, None),
    ("entity_types", dict, EntitiesComparerTemplates.entity_types_comparer),
    ("must_reach", bool, None),
    ("priority", int, None),
))

dig_comparer =\
("minecraft:behavior.dig", dict, Comparer.UnnamedDictComparerSection(
    ("digs_in_daylight", bool, None),
    ("duration", decimal, None),
    ("idle_time", decimal, None),
    ("on_start", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("suspicion_is_disturbance", bool, None),
    ("vibration_is_disturbance", bool, None),
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

drink_milk_comparer =\
("minecraft:behavior.drink_milk", dict, Comparer.UnnamedDictComparerSection(
    ("filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("priority", int, None),
))

drink_potion_comparer =\
("minecraft:behavior.drink_potion", dict, Comparer.UnnamedDictComparerSection(
    ("potions", list, Comparer.ListComparerSection(
        name="potion",
        ordered=False,
        measure_length=True,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("chance", decimal, None),
            ("filters", dict, EntitiesComparerTemplates.filter_comparer),
            ("id", int, None),
        )
    )),
    ("priority", int, None),
    ("speed_modifier", decimal, None),
))

drop_item_for_comparer =\
("minecraft:behavior.drop_item_for", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown", decimal, None),
    ("drop_item_chance", decimal, None),
    ("entity_types", list, EntitiesComparerTemplates.entity_types_comparers),
    ("goal_radius", decimal, None),
    ("loot_table", str, None),
    ("max_head_look_at_height", decimal, None),
    ("minimum_teleport_distance", decimal, None),
    ("offering_distance", decimal, None),
    ("on_drop_attempt", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("search_count", int, None),
    ("search_height", int, None),
    ("search_range", int, None),
    ("seconds_before_pickup", decimal, None),
    ("speed_multiplier", decimal, None),
    ("target_range", list, EntitiesComparerTemplates.coordinate_comparer),
    ("teleport_offset", list, EntitiesComparerTemplates.coordinate_comparer),
    ("time_of_day_range", list, EntitiesComparerTemplates.range_comparer),
))

eat_carried_item_comparer =\
("minecraft:behavior.eat_carried_item", dict, Comparer.UnnamedDictComparerSection(
    ("delay_before_eating", int, None),
    ("priority", int, None),
))

eat_mob_comparer =\
("minecraft:behavior.eat_mob", dict, Comparer.UnnamedDictComparerSection(
    ("eat_animation_time", decimal, None),
    ("eat_mob_sound", str, None),
    ("loot_table", str, None),
    ("priority", int, None),
    ("pull_in_force", decimal, None),
    ("reach_mob_distance", decimal, None),
    ("run_speed", decimal, None),
))

emerge_comparer =\
("minecraft:behavior.emerge", dict, Comparer.UnnamedDictComparerSection(
    ("duration", decimal, None),
    ("on_done", dict, EntitiesComparerTemplates.event_target_comparer),
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

explore_outskirts_behavior =\
("minecraft:behavior.explore_outskirts", dict, Comparer.UnnamedDictComparerSection(
    ("dist_from_boundary", list, EntitiesComparerTemplates.coordinate_comparer),
    ("explore_dist", decimal, None),
    ("max_travel_time", decimal, None),
    ("max_wait_time", decimal, None),
    ("min_dist_from_target", decimal, None),
    ("min_perimeter", decimal, None),
    ("min_wait_time", decimal, None),
    ("next_xz", int, None),
    ("next_y", int, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
    ("timer_ratio", decimal, None),
))

fertilize_farm_block_comparer =\
("minecraft:behavior.fertilize_farm_block", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

find_cover_comparer =\
("minecraft:behavior.find_cover", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_time", decimal, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

find_mount_comparer =\
("minecraft:behavior.find_mount", dict, Comparer.UnnamedDictComparerSection(
    ("avoid_water", bool, None),
    ("max_failed_attempts", int, None),
    ("mount_distance", decimal, None),
    ("priority", int, None),
    ("start_delay", int, None),
    ("target_needed", bool, None),
    ("within_radius", int, None),
))

find_underwater_treasure_comparer =\
("minecraft:behavior.find_underwater_treasure", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("search_range", int, None),
    ("speed_multiplier", decimal, None),
    ("stop_distance", int, None),
))

fire_at_target_comparer =\
("minecraft:behavior.fire_at_target", dict, Comparer.UnnamedDictComparerSection(
    ("attack_cooldown", decimal, None),
    ("attack_range", list, EntitiesComparerTemplates.range_comparer),
    ("owner_anchor", int, None),
    ("owner_offset", list, EntitiesComparerTemplates.coordinate_comparer),
    ("post_shoot_delay", decimal, None),
    ("pre_shoot_delay", decimal, None),
    ("priority", int, None),
    ("projectile_def", str, None),
    ("ranged_fov", decimal, None),
    ("target_anchor", int, None),
    ("target_offset", list, EntitiesComparerTemplates.coordinate_comparer),
))

flee_sun_comparer =\
("minecraft:behavior.flee_sun", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

float_comparer =\
("minecraft:behavior.float", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("sink_with_passengers", bool, None),
))

float_wander_comparer =\
("minecraft:behavior.float_wander", dict, Comparer.UnnamedDictComparerSection(
    ("float_duration", list, EntitiesComparerTemplates.range_comparer),
    ("must_reach", bool, None),
    ("priority", int, None),
    ("random_reselect", bool, None),
    ("xz_dist", int, None),
    ("y_dist", int, None),
    ("y_offset", decimal, None),
))

follow_caravan_comparer =\
("minecraft:behavior.follow_caravan", dict, Comparer.UnnamedDictComparerSection(
    ("entity_count", int, None),
    ("entity_types", (dict, list), EntitiesComparerTemplates.entity_types_comparers),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

follow_mob_comparer =\
("minecraft:behavior.follow_mob", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
    ("stop_distance", int, None),
    ("search_range", int, None),
))

follow_owner_comparer =\
("minecraft:behavior.follow_owner", dict, Comparer.UnnamedDictComparerSection(
    ("can_teleport", bool, None),
    ("ignore_vibration", bool, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
    ("start_distance", int, None),
    ("stop_distance", int, None),
))

follow_parent_comparer =\
("minecraft:behavior.follow_parent", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

follow_target_captain_comparer =\
("minecraft:behavior.follow_target_captain", dict, Comparer.UnnamedDictComparerSection(
    ("follow_distance", int, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
    ("within_radius", int, None),
))

go_and_give_items_to_noteblock_comparer =\
("minecraft:behavior.go_and_give_items_to_noteblock", dict, Comparer.UnnamedDictComparerSection(
    ("on_item_throw", list, EntitiesComparerTemplates.event_target_list_comparer),
    ("priority", int, None),
    ("run_speed", int, None),
    ("throw_sound", str, None),
))

go_and_give_items_to_owner_comparer =\
("minecraft:behavior.go_and_give_items_to_owner", dict, Comparer.UnnamedDictComparerSection(
    ("on_item_throw", list, EntitiesComparerTemplates.event_target_list_comparer),
    ("priority", int, None),
    ("run_speed", int, None),
    ("throw_sound", str, None),
))

go_home_comparer =\
("minecraft:behavior.go_home", dict, Comparer.UnnamedDictComparerSection(
    ("goal_radius", decimal, None),
    ("interval", int, None),
    ("on_failed", (dict, list), [
        (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.event_target_comparer),
        (lambda key, value: isinstance(value, list), EntitiesComparerTemplates.event_target_list_comparer),
    ]),
    ("on_home", list, EntitiesComparerTemplates.event_target_filters_list_comparer),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

guardian_attack_comparer =\
("minecraft:behavior.guardian_attack", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

harvest_farm_block_comparer =\
("minecraft:behavior.harvest_farm_block", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

hide_comparer =\
("minecraft:behavior.hide", dict, Comparer.UnnamedDictComparerSection(
    ("duration", decimal, None),
    ("poi_type", str, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

hold_ground_comparer =\
("minecraft:behavior.hold_ground", dict, Comparer.UnnamedDictComparerSection(
    ("broadcast", bool, None),
    ("broadcast_range", int, None),
    ("min_radius", int, None),
    ("priority", int, None),
    ("within_radius_event", dict, EntitiesComparerTemplates.event_target_comparer),
))

hurt_by_target_comparer =\
("minecraft:behavior.hurt_by_target", dict, Comparer.UnnamedDictComparerSection(
    ("alert_same_type", bool, None),
    ("entity_types", (dict, list), EntitiesComparerTemplates.entity_types_comparers),
    ("hurt_owner", bool, None),
    ("priority", int, None),
))

inspect_bookshelf_comparer =\
("minecraft:behavior.inspect_bookshelf", dict, Comparer.UnnamedDictComparerSection(
    ("goal_radius", decimal, None),
    ("priority", int, None),
    ("search_count", int, None),
    ("search_height", int, None),
    ("search_range", int, None),
    ("speed_multiplier", decimal, None),
))

investigate_suspicious_location_comparer =\
("minecraft:behavior.investigate_suspicious_location", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

jump_around_target_comparer =\
("minecraft:behavior.jump_around_target", dict, Comparer.UnnamedDictComparerSection(
    ("check_collision", bool, None),
    ("entity_bounding_box_scale", decimal, None),
    ("filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("jump_angles", list, Comparer.ListComparerSection(
        name="angle",
        measure_length=True,
        ordered=False,
        print_flat=True,
        comparer=None,
        types=(decimal,),
    )),
    ("jump_cooldown_duration", decimal, None),
    ("jump_cooldown_when_hurt_duration", decimal, None),
    ("landing_distance_from_target", list, EntitiesComparerTemplates.range_comparer),
    ("landing_position_spread_degrees", int, None),
    ("last_hurt_duration", decimal, None),
    ("line_of_sight_obstruction_height_ignore", int, None),
    ("max_jump_velocity", decimal, None),
    ("prepare_jump_duration", decimal, None),
    ("priority", int, None),
    ("required_vertical_space", int, None),
    ("snap_to_surface_block_range", int, None),
    ("valid_distance_to_target", list, EntitiesComparerTemplates.range_comparer),
))

jump_to_block_comparer =\
("minecraft:behavior.jump_to_block", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_range", list, EntitiesComparerTemplates.range_comparer),
    ("forbidden_blocks", list, EntitiesComparerTemplates.block_list_comparer),
    ("max_velocity", decimal, None),
    ("minimum_distance", int, None),
    ("minimum_path_length", int, None),
    ("preferred_blocks", list, EntitiesComparerTemplates.block_list_comparer),
    ("preferred_blocks_chance", decimal, None),
    ("priority", int, None),
    ("scale_factor", decimal, None),
    ("search_height", int, None),
    ("search_width", int, None),
))

knockback_roar =\
("minecraft:behavior.knockback_roar", dict, Comparer.UnnamedDictComparerSection(
    ("attack_time", decimal, None),
    ("cooldown_time", decimal, None),
    ("damage_filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("duration", int, None),
    ("knockback_damage", int, None),
    ("knockback_filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("knockback_horizontal_strength", int, None),
    ("knockback_range", int, None),
    ("knockback_vertical_strength", int, None),
    ("on_roar_end", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
))

lay_down_comparer =\
("minecraft:behavior.lay_down", dict, Comparer.UnnamedDictComparerSection(
    ("interval", int, None),
    ("priority", int, None),
    ("random_stop_interval", int, None),
))

lay_egg_comparer =\
("minecraft:behavior.lay_egg", dict, Comparer.UnnamedDictComparerSection(
    ("allow_laying_from_below", bool, None),
    ("egg_type", str, None),
    ("goal_radius", decimal, None),
    ("lay_egg_sound", str, None),
    ("lay_seconds", int, None),
    ("on_lay", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("search_height", int, None),
    ("search_range", int, None),
    ("speed_multiplier", decimal, None),
    ("target_blocks", list, EntitiesComparerTemplates.block_list_comparer),
    ("target_materials_above_block", list, Comparer.ListComparerSection(
        name="material",
        measure_length=True,
        ordered=False,
        types=(str,),
        comparer=None
    )),
    ("use_default_animation", bool, None),
))

leap_at_target_comparer =\
("minecraft:behavior.leap_at_target", dict, Comparer.UnnamedDictComparerSection(
    ("must_be_on_ground", bool, None),
    ("priority", int, None),
    ("target_dist", decimal, None),
    ("yd", decimal, None),
))

look_at_entity_comparer =\
("minecraft:behavior.look_at_entity", dict, Comparer.UnnamedDictComparerSection(
    ("angle_of_view_horizontal", int, None),
    ("angle_of_view_vertical", int, None),
    ("filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("look_distance", decimal, None),
    ("priority", int, None),
    ("probability", decimal, None),
))

look_at_player_comparer =\
("minecraft:behavior.look_at_player", dict, Comparer.UnnamedDictComparerSection(
    ("angle_of_view_horizontal", int, None),
    ("look_distance", decimal, None),
    ("max_look_time", int, None),
    ("min_look_time", int, None),
    ("priority", int, None),
    ("probability", decimal, None),
    ("target_distance", decimal, None),
))

look_at_target =\
("minecraft:behavior.look_at_target", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

look_at_trading_player_comparer =\
("minecraft:behavior.look_at_trading_player", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

make_love_comparer =\
("minecraft:behavior.make_love", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

melee_attack_comparer =\
("minecraft:behavior.melee_attack", dict, Comparer.UnnamedDictComparerSection(
    ("max_dist", int, None),
    ("melee_fov", int, None),
    ("on_kill", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("random_stop_interval", decimal, None),
    ("reach_multiplier", decimal, None),
    ("speed_multiplier", decimal, None),
    ("track_target", bool, None),
))

melee_box_attack_comparer =\
("minecraft:behavior.melee_box_attack", dict, Comparer.UnnamedDictComparerSection(
    ("attack_once", bool, None),
    ("can_spread_on_fire", bool, None),
    ("cooldown_time", decimal, None),
    ("melee_fov", int, None),
    ("on_attack", dict, EntitiesComparerTemplates.event_target_comparer),
    ("on_kill", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("random_stop_interval", int, None),
    ("require_complete_path", bool, None),
    ("speed_multiplier", decimal, None),
    ("track_target", bool, None),
))

mingle_comparer =\
("minecraft:behavior.mingle", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_time", int, None),
    ("duration", int, None),
    ("mingle_partner_type", str, None),
    ("mingle_distance", decimal, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

mount_pathing_comparer =\
("minecraft:behavior.mount_pathing", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
    ("target_dist", decimal, None),
    ("track_target", bool, None),
))

move_away_from_target =\
("minecraft:behavior.move_away_from_target", dict, Comparer.UnnamedDictComparerSection(
    ("destination_pos_spread_degrees", int, None),
    ("destination_position_range", list, EntitiesComparerTemplates.range_comparer),
    ("filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("movement_speed", decimal, None),
    ("priority", int, None),
))

move_indoors_comparer =\
("minecraft:behavior.move_indoors", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
    ("timeout_cooldown", decimal, None),
))

move_outdoors_comparer =\
("minecraft:behavior.move_outdoors", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
    ("timeout_cooldown", decimal, None),
))

move_to_block_comparer =\
("minecraft:behavior.move_to_block", dict, Comparer.UnnamedDictComparerSection(
    ("goal_radius", decimal, None),
    ("on_reach", list, EntitiesComparerTemplates.event_target_list_comparer),
    ("on_stay_completed", list, EntitiesComparerTemplates.event_target_list_comparer),
    ("priority", int, None),
    ("search_height", int, None),
    ("search_range", int, None),
    ("start_chance", decimal, None),
    ("stay_duration", decimal, None),
    ("target_block_filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("target_blocks", list, EntitiesComparerTemplates.block_list_comparer),
    ("target_offset", list, EntitiesComparerTemplates.coordinate_comparer),
    ("target_selection_method", str, None),
    ("tick_interval", int, None),
))

move_to_land_comparer =\
("minecraft:behavior.move_to_land", dict, Comparer.UnnamedDictComparerSection(
    ("goal_radius", decimal, None),
    ("priority", int, None),
    ("search_count", int, None),
    ("search_height", int, None),
    ("search_range", int, None),
))

move_to_lava_comparer =\
("minecraft:behavior.move_to_lava", dict, Comparer.UnnamedDictComparerSection(
    ("goal_radius", decimal, None),
    ("priority", int, None),
    ("search_count", int, None),
    ("search_height", int, None),
    ("search_range", int, None),
))

move_to_liquid_comparer =\
("minecraft:behavior.move_to_liquid", dict, Comparer.UnnamedDictComparerSection(
    ("goal_radius", decimal, None),
    ("priority", int, None),
    ("material_type", str, None),
    ("search_count", int, None),
    ("search_height", int, None),
    ("search_range", int, None),
))

move_to_random_block_comparer =\
("minecraft:behavior.move_to_random_block", dict, Comparer.UnnamedDictComparerSection(
    ("block_distance", int, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
    ("within_radius", int, None),
))

move_through_village_comparer =\
("minecraft:behavior.move_through_village", dict, Comparer.UnnamedDictComparerSection(
    ("only_at_night", bool, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

move_to_village_comparer =\
("minecraft:behavior.move_to_village", dict, Comparer.UnnamedDictComparerSection(
    ("goal_radius", decimal, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

move_to_water_comparer =\
("minecraft:behavior.move_to_water", dict, Comparer.UnnamedDictComparerSection(
    ("goal_radius", decimal, None),
    ("priority", int, None),
    ("search_count", int, None),
    ("search_height", int, None),
    ("search_range", int, None),
))

move_towards_dwelling_restriction_comparer =\
("minecraft:behavior.move_towards_dwelling_restriction", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

move_towards_home_restriction_comparer =\
("minecraft:behavior.move_towards_home_restriction", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

move_towards_target_comparer =\
("minecraft:behavior.move_towards_target", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
    ("within_radius", int, None),
))

nap_comparer =\
("minecraft:behavior.nap", dict, Comparer.UnnamedDictComparerSection(
    ("can_nap_filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("cooldown_max", decimal, None),
    ("cooldown_min", decimal, None),
    ("mob_detect_dist", decimal, None),
    ("mob_detect_height", decimal, None),
    ("priority", int, None),
    ("wake_mob_exceptions", dict, EntitiesComparerTemplates.filter_comparer),
))

nearest_attackable_target_comparer =\
("minecraft:behavior.nearest_attackable_target", dict, Comparer.UnnamedDictComparerSection(
    ("attack_interval", int, None),
    ("attack_interval_min", decimal, None),
    ("entity_types", (dict, list), EntitiesComparerTemplates.entity_types_comparers),
    ("must_reach", bool, None),
    ("must_see", bool, None),
    ("must_see_forget_duration", decimal, None),
    ("persist_time", decimal, None),
    ("priority", int, None),
    ("reselect_targets", bool, None),
    ("scan_interval", int, None),
    ("target_search_height", decimal, None),
    ("within_radius", decimal, None),
))

nearest_prioritized_attackable_target_comparer =\
("minecraft:behavior.nearest_prioritized_attackable_target", dict, Comparer.UnnamedDictComparerSection(
    ("attack_interval", int, None),
    ("entity_types", list, EntitiesComparerTemplates.entity_types_comparers),
    ("must_reach", bool, None),
    ("must_see", bool, None),
    ("persist_time", decimal, None),
    ("priority", int, None),
    ("reselect_targets", bool, None),
    ("target_search_height", int, None),
    ("within_radius", decimal, None),
))

ocelot_sit_on_block_comparer =\
("minecraft:behavior.ocelot_sit_on_block", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

ocelotattack_comparer =\
("minecraft:behavior.ocelotattack", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_time", decimal, None),
    ("max_distance", decimal, None),
    ("max_sneak_range", decimal, None),
    ("max_sprint_range", decimal, None),
    ("priority", int, None),
    ("reach_multiplier", decimal, None),
    ("sneak_speed_multiplier", decimal, None),
    ("sprint_speed_multiplier", decimal, None),
    ("walk_speed_multiplier", decimal, None),
    ("x_max_rotation", decimal, None),
    ("y_max_head_rotation", decimal, None),
))

offer_flower_comparer =\
("minecraft:behavior.offer_flower", dict, Comparer.UnnamedDictComparerSection(
    ("filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("priority", int, None),
))

open_door_comparer =\
("minecraft:behavior.open_door", dict, Comparer.UnnamedDictComparerSection(
    ("close_door_after", bool, None),
    ("priority", int, None),
))

owner_hurt_by_target_comparer =\
("minecraft:behavior.owner_hurt_by_target", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

owner_hurt_target_comparer =\
("minecraft:behavior.owner_hurt_target", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

panic_comparer =\
("minecraft:behavior.panic", dict, Comparer.UnnamedDictComparerSection(
    ("force", bool, None),
    ("ignore_mob_damage", bool, None),
    ("panic_sound", str, None),
    ("prefer_water", bool, None),
    ("priority", int, None),
    ("sound_interval", dict, EntitiesComparerTemplates.range_dict_comparer),
    ("speed_multiplier", decimal, None),
))

pet_sleep_with_owner_comparer =\
("minecraft:behavior.pet_sleep_with_owner", dict, Comparer.UnnamedDictComparerSection(
    ("goal_radius", decimal, None),
    ("priority", int, None),
    ("search_height", int, None),
    ("search_radius", int, None),
    ("speed_multiplier", decimal, None),
))

pickup_items_comparer =\
("minecraft:behavior.pickup_items", dict, Comparer.UnnamedDictComparerSection(
    ("can_pickup_any_item", bool, None),
    ("can_pickup_to_hand_or_equipment", bool, None),
    ("cooldown_after_being_attacked", decimal, None),
    ("excluded_items", list, EntitiesComparerTemplates.item_list_comparer),
    ("goal_radius", decimal, None),
    ("max_dist", int, None),
    ("pickup_based_on_chance", bool, None),
    ("pickup_same_items_as_in_hand", bool, None),
    ("priority", int, None),
    ("search_height", int, None),
    ("speed_multiplier", decimal, None),
))

play_comparer =\
("minecraft:behavior.play", dict, Comparer.UnnamedDictComparerSection(
    ("friend_types", list, Comparer.ListComparerSection(
        name="filter",
        ordered=False,
        measure_length=True,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("filters", dict, EntitiesComparerTemplates.filter_comparer),
        )
    )),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

play_dead_comparer =\
("minecraft:behavior.play_dead", dict, Comparer.UnnamedDictComparerSection(
    ("apply_regeneration", bool, None),
    ("damage_sources", list, Comparer.ListComparerSection(
        name="damage source",
        print_flat=True,
        measure_length=True,
        ordered=False,
        comparer=None,
        types=(str,),
    )),
    ("duration", int, None),
    ("filters", dict, EntitiesComparerTemplates.filter_comparer),
    ("force_below_health", int, None),
    ("priority", int, None),
    ("random_damage_range", list, EntitiesComparerTemplates.range_comparer),
    ("random_start_chance", decimal, None),
))

player_ride_tamed_comparer =\
("minecraft:behavior.player_ride_tamed", dict, Comparer.UnnamedDictComparerSection())

raid_garden_comparer =\
("minecraft:behavior.raid_garden", dict, Comparer.UnnamedDictComparerSection(
    ("blocks", list, EntitiesComparerTemplates.block_list_comparer),
    ("goal_radius", decimal, None),
    ("initial_eat_delay", int, None),
    ("max_to_eat", int, None),
    ("priority", int, None),
    ("search_height", int, None),
    ("search_range", int, None),
    ("speed_multiplier", decimal, None),
))

ram_attack_comparer =\
("minecraft:behavior.ram_attack", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_range", list, EntitiesComparerTemplates.range_comparer),
    ("knockback_force", decimal, None),
    ("knockback_height", decimal, None),
    ("min_ram_distance", int, None),
    ("on_start", list, EntitiesComparerTemplates.event_target_list_comparer),
    ("pre_ram_sound", str, None),
    ("priority", int, None),
    ("ram_distance", int, None),
    ("ram_impact_sound", str, None),
    ("ram_speed", decimal, None),
    ("run_speed", decimal, None),
))

random_breach_comparer =\
("minecraft:behavior.random_breach", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_time", decimal, None),
    ("interval", int, None),
    ("priority", int, None),
    ("xz_dist", int, None),
))

random_fly_comparer =\
("minecraft:behavior.random_fly", dict, Comparer.UnnamedDictComparerSection(
    ("avoid_damage_blocks", bool, None),
    ("can_land_on_trees", bool, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
    ("xz_dist", int, None),
    ("y_dist", int, None),
    ("y_offset", int, None),
))

random_hover_comparer =\
("minecraft:behavior.random_hover", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("xz_dist", int, None),
    ("y_dist", int, None),
    ("y_offset", int, None),
    ("interval", int, None),
    ("hover_height", list, EntitiesComparerTemplates.range_comparer),
))

random_look_around_comparer =\
("minecraft:behavior.random_look_around", dict, Comparer.UnnamedDictComparerSection(
    ("look_distance", decimal, None),
    ("priority", int, None),
))

random_look_around_and_sit_comparer =\
("minecraft:behavior.random_look_around_and_sit", dict, Comparer.UnnamedDictComparerSection(
    ("continue_if_leashed", bool, None),
    ("continue_sitting_on_reload", bool, None),
    ("max_angle_of_view_horizontal", int, None),
    ("max_look_count", int, None),
    ("max_look_time", int, None),
    ("min_angle_of_view_horizontal", int, None),
    ("min_look_count", int, None),
    ("min_look_time", int, None),
    ("priority", int, None),
    ("probability", decimal, None),
    ("random_look_around_cooldown", int, None),
))

random_search_and_dig_comparer =\
("minecraft:behavior.random_search_and_dig", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_range", decimal, None),
    ("digging_duration_range", list, EntitiesComparerTemplates.range_comparer),
    ("find_valid_position_retries", int, None),
    ("goal_radius", decimal, None),
    ("item_table", str, None),
    ("on_digging_start", dict, EntitiesComparerTemplates.event_target_comparer),
    ("on_fail_during_digging", dict, EntitiesComparerTemplates.event_target_comparer),
    ("on_fail_during_searching", dict, EntitiesComparerTemplates.event_target_comparer),
    ("on_item_found", dict, EntitiesComparerTemplates.event_target_comparer),
    ("on_searching_start", dict, EntitiesComparerTemplates.event_target_comparer),
    ("on_success", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("search_range_xz", decimal, None),
    ("search_range_y", int, None),
    ("spawn_item_after_seconds", decimal, None),
    ("spawn_item_pos_offset", decimal, None),
    ("speed_multiplier", decimal, None),
    ("target_blocks", list, EntitiesComparerTemplates.block_list_comparer),
))

random_sitting_comparer =\
("minecraft:behavior.random_sitting", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown", int, None),
    ("min_sit_time", int, None),
    ("priority", int, None),
    ("start_chance", decimal, None),
    ("stop_chance", decimal, None),
))

random_stroll_comparer =\
("minecraft:behavior.random_stroll", dict, Comparer.UnnamedDictComparerSection(
    ("interval", int, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
    ("xz_dist", int, None),
    ("y_dist", int, None),
))

random_swim_comparer =\
("minecraft:behavior.random_swim", dict, Comparer.UnnamedDictComparerSection(
    ("avoid_surface", bool, None),
    ("interval", int, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
    ("xz_dist", int, None),
    ("y_dist", int, None),
))

ranged_attack_comparer =\
("minecraft:behavior.ranged_attack", dict, Comparer.UnnamedDictComparerSection(
    ("attack_interval", decimal, None),
    ("attack_interval_max", decimal, None),
    ("attack_interval_min", decimal, None),
    ("attack_radius", decimal, None),
    ("attack_radius_min", decimal, None),
    ("burst_interval", decimal, None),
    ("burst_shots", int, None),
    ("charge_charged_trigger", decimal, None),
    ("charge_shoot_trigger", decimal, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
    ("swing", bool, None),
    ("target_in_sight_time", decimal, None),
))

ravager_blocked_comparer =\
("minecraft:ravager_blocked", dict, Comparer.UnnamedDictComparerSection(
    ("knockback_strength", decimal, None),
    ("reaction_choices", list, Comparer.ListComparerSection(
        name="choice",
        measure_length=True,
        ordered=False,
        types=(dict,),
        comparer=Comparer.UnnamedDictComparerSection(
            ("value", dict, EntitiesComparerTemplates.event_target_comparer),
            ("weight", int, None),
        )
    ))
))

receive_love_comparer =\
("minecraft:behavior.receive_love", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

restrict_open_door_comparer =\
("minecraft:behavior.restrict_open_door", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

rise_to_liquid_level =\
("minecraft:behavior.rise_to_liquid_level", dict, Comparer.UnnamedDictComparerSection(
    ("liquid_y_offset", decimal, None),
    ("priority", int, None),
    ("rise_delta", decimal, None),
    ("sink_delta", decimal, None),
))

roar_comparer =\
("minecraft:behavior.roar", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("duration", decimal, None),
))

roll_comparer =\
("minecraft:behavior.roll", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("probability", decimal, None),
))

run_around_like_crazy_comparer =\
("minecraft:behavior.run_around_like_crazy", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

scared_comparer =\
("minecraft:behavior.scared", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("sound_interval", int, None),
))

send_event_comparer =\
("minecraft:behavior.send_event", dict, Comparer.UnnamedDictComparerSection(
    ("event_choices", list, EntitiesComparerTemplates.choice_comparer),
    ("priority", int, None),
))

share_items_comparer =\
("minecraft:behavior.share_items", dict, Comparer.UnnamedDictComparerSection(
    ("entity_types", (dict, list), EntitiesComparerTemplates.entity_types_comparers),
    ("goal_radius", decimal, None),
    ("max_dist", int, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

silverfish_merge_with_stone_comparer =\
("minecraft:behavior.silverfish_merge_with_stone", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

silverfish_wake_up_friends_comparer =\
("minecraft:behavior.silverfish_wake_up_friends", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

skeleton_horse_trap_comparer =\
("minecraft:behavior.skeleton_horse_trap", dict, Comparer.UnnamedDictComparerSection(
    ("duration", decimal, None),
    ("priority", int, None),
    ("within_radius", decimal, None),
))

sleep_comparer =\
("minecraft:behavior.sleep", dict, Comparer.UnnamedDictComparerSection(
    ("goal_radius", decimal, None),
    ("priority", int, None),
    ("sleep_collider_height", decimal, None),
    ("sleep_collider_width", decimal, None),
    ("sleep_y_offset", decimal, None),
    ("speed_multiplier", decimal, None),
    ("timeout_cooldown", decimal, None),
))

slime_attack_comparer =\
("minecraft:behavior.slime_attack", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

slime_float_comparer =\
("minecraft:behavior.slime_float", dict, Comparer.UnnamedDictComparerSection(
    ("jump_chance_percentage", decimal, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

slime_keep_on_jumping_comparer =\
("minecraft:behavior.slime_keep_on_jumping", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

slime_random_direction_comparer =\
("minecraft:behavior.slime_random_direction", dict, Comparer.UnnamedDictComparerSection(
    ("add_random_time_range", int, None),
    ("min_change_direction_time", decimal, None),
    ("priority", int, None),
    ("turn_range", int, None),
))

snacking_comparer =\
("minecraft:behavior.snacking", dict, Comparer.UnnamedDictComparerSection(
    ("items", list, EntitiesComparerTemplates.item_list_comparer),
    ("priority", int, None),
    ("snacking_cooldown", decimal, None),
    ("snacking_cooldown_min", int, None),
    ("snacking_stop_chance", decimal, None),
))

sneeze_comparer =\
("minecraft:behavior.sneeze", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_time", decimal, None),
    ("drop_item_chance", decimal, None),
    ("entity_types", list, EntitiesComparerTemplates.entity_types_comparers),
    ("loot_table", str, None),
    ("priority", int, None),
    ("prepare_sound", str, None),
    ("prepare_time", decimal, None),
    ("probability", decimal, None),
    ("sound", str, None),
    ("within_radius", decimal, None),
))

sonic_boom_comparer =\
("minecraft:behavior.sonic_boom", dict, Comparer.UnnamedDictComparerSection(
    ("attack_cooldown", int, None),
    ("attack_damage", int, None),
    ("attack_range_horizontal", int, None),
    ("attack_range_vertical", int, None),
    ("attack_sound", str, None),
    ("charge_sound", str, None),
    ("duration", decimal, None),
    ("duration_until_attack_sound", decimal, None),
    ("knockback_height_cap", decimal, None),
    ("knockback_horizontal_strength", decimal, None),
    ("knockback_vertical_strength", decimal, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

sniff_comparer =\
("minecraft:behavior.sniff", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_range", list, EntitiesComparerTemplates.range_comparer),
    ("duration", decimal, None),
    ("priority", int, None),
    ("sniffing_radius", decimal, None),
    ("suspicion_radius_horizontal", decimal, None),
    ("suspicion_radius_vertical", decimal, None),
))

squid_dive_comparer =\
("minecraft:behavior.squid_dive", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

squid_flee_comparer =\
("minecraft:behavior.squid_flee", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

squid_idle_comparer =\
("minecraft:behavior.squid_idle", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

squid_move_away_from_ground_comparer =\
("minecraft:behavior.squid_move_away_from_ground", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

squid_out_of_water_comparer =\
("minecraft:behavior.squid_out_of_water", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

stalk_and_pounce_on_target_comparer =\
("minecraft:behavior.stalk_and_pounce_on_target", dict, Comparer.UnnamedDictComparerSection(
    ("interest_time", decimal, None),
    ("leap_dist", decimal, None),
    ("leap_height", decimal, None),
    ("max_stalk_dist", decimal, None),
    ("pounce_max_dist", decimal, None),
    ("priority", int, None),
    ("stalk_speed", decimal, None),
    ("strike_dist", decimal, None),
    ("stuck_blocks", dict, EntitiesComparerTemplates.filter_comparer),
    ("stuck_time", decimal, None),
))

stay_near_noteblock_comparer =\
("minecraft:behavior.stay_near_noteblock", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed", int, None),
    ("start_distance", int, None),
    ("stop_distance", int, None),
))

stay_while_sitting_comparer =\
("minecraft:behavior.stay_while_sitting", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

stomp_attack_comparer =\
("minecraft:behavior.stomp_attack", dict, Comparer.UnnamedDictComparerSection(
    ("no_damage_range_multiplier", decimal, None),
    ("priority", int, None),
    ("require_complete_path", bool, None),
    ("stomp_range_multiplier", decimal, None),
    ("track_target", bool, None),
))

stomp_turtle_egg_comparer =\
("minecraft:behavior.stomp_turtle_egg", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
    ("search_range", int, None),
    ("search_height", int, None),
    ("goal_radius", decimal, None),
    ("interval", int, None),
))

stroll_towards_village_comparer =\
("minecraft:behavior.stroll_towards_village", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_time", decimal, None),
    ("goal_radius", decimal, None),
    ("priority", int, None),
    ("search_range", int, None),
    ("speed_multiplier", decimal, None),
    ("start_chance", decimal, None),
))

summon_entity_comparer =\
("minecraft:behavior.summon_entity", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("summon_choices", list, EntitiesComparerTemplates.choice_comparer),
))

swell_comparer =\
("minecraft:behavior.swell", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("start_distance", decimal, None),
    ("stop_distance", decimal, None),
))

swim_idle_comparer =\
("minecraft:behavior.swim_idle", dict, Comparer.UnnamedDictComparerSection(
    ("idle_time", decimal, None),
    ("priority", int, None),
    ("success_rate", decimal, None),
))

swim_wander_comparer =\
("minecraft:behavior.swim_wander", dict, Comparer.UnnamedDictComparerSection(
    ("interval", decimal, None),
    ("look_ahead", decimal, None),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
    ("wander_time", decimal, None),
))

swim_with_entity_comparer =\
("minecraft:behavior.swim_with_entity", dict, Comparer.UnnamedDictComparerSection(
    ("catch_up_multiplier", decimal, None),
    ("catch_up_threshold", decimal, None),
    ("chance_to_stop", decimal, None),
    ("entity_types", list, EntitiesComparerTemplates.entity_types_comparers),
    ("match_direction_threshold", decimal, None),
    ("priority", int, None),
    ("search_range", decimal, None),
    ("speed_multiplier", decimal, None),
    ("state_check_interval", decimal, None),
    ("stop_distance", decimal, None),
    ("success_rate", decimal, None),
))

swoop_attack_comparer =\
("minecraft:behavior.swoop_attack", dict, Comparer.UnnamedDictComparerSection(
    ("damage_reach", decimal, None),
    ("delay_range", list, EntitiesComparerTemplates.range_comparer),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
))

take_flower_comparer =\
("minecraft:behavior.take_flower", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
    ("filters", dict, EntitiesComparerTemplates.filter_comparer),
))

target_when_pushed_comparer =\
("minecraft:behavior.target_when_pushed", dict, Comparer.UnnamedDictComparerSection(
    ("entity_types", (dict, list), EntitiesComparerTemplates.entity_types_comparers),
    ("percent_chance", decimal, None),
    ("priority", int, None),
))

tempt_comparer =\
("minecraft:behavior.tempt", dict, Comparer.UnnamedDictComparerSection(
    ("can_get_scared", bool, None),
    ("can_tempt_vertically", bool, None),
    ("can_tempt_while_ridden", bool, None),
    ("items", list, EntitiesComparerTemplates.item_list_comparer),
    ("priority", int, None),
    ("sound_interval", (dict, list), [
        (lambda key, value: isinstance(value, dict), EntitiesComparerTemplates.range_dict_comparer),
        (lambda key, value: isinstance(value, list), EntitiesComparerTemplates.range_comparer),
    ]),
    ("speed_multiplier", decimal, None),
    ("tempt_sound", str, None),
    ("within_radius", int, None),
))

timer_flag_1_comparer =\
("minecraft:behavior.timer_flag_1", dict, Comparer.UnnamedDictComparerSection(
    ("control_flags", list, Comparer.ListComparerSection(
        name="control_flag",
        ordered=False,
        measure_length=True,
        types=(str,),
        comparer=None,
    )),
    ("cooldown_range", list, EntitiesComparerTemplates.range_comparer),
    ("duration_range", decimal, None),
    ("on_end", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
))

timer_flag_2_comparer =\
("minecraft:behavior.timer_flag_2", dict, Comparer.UnnamedDictComparerSection(
    ("control_flags", list, Comparer.ListComparerSection(
        name="control_flag",
        measure_length=True,
        ordered=False,
        types=(str,),
        comparer=None,
    )),
    ("cooldown_range", decimal, None),
    ("duration_range", list, EntitiesComparerTemplates.range_comparer),
    ("on_end", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
))

timer_flag_3_comparer =\
("minecraft:behavior.timer_flag_3", dict, Comparer.UnnamedDictComparerSection(
    ("cooldown_range", decimal, None),
    ("duration_range", list, EntitiesComparerTemplates.range_comparer),
    ("on_end", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
))

trade_interest_comparer =\
("minecraft:behavior.trade_interest", dict, Comparer.UnnamedDictComparerSection(
    ("carried_item_switch_time", decimal, None),
    ("cooldown", decimal, None),
    ("interest_time", decimal, None),
    ("priority", int, None),
    ("remove_item_time", decimal, None),
    ("within_radius", decimal, None),
))

wither_random_attack_pos_goal_comparer =\
("minecraft:behavior.wither_random_attack_pos_goal", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

wither_target_highest_damage_comparer =\
("minecraft:behavior.wither_target_highest_damage", dict, Comparer.UnnamedDictComparerSection(
    ("priority", int, None),
))

work_comparer =\
("minecraft:behavior.work", dict, Comparer.UnnamedDictComparerSection(
    ("active_time", int, None),
    ("can_work_in_rain", bool, None),
    ("goal_cooldown", int, None),
    ("on_arrival", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("sound_delay_max", int, None),
    ("sound_delay_min", int, None),
    ("speed_multiplier", decimal, None),
    ("work_in_rain_tolerance", int, None),
))

work_composter_comparer =\
("minecraft:behavior.work_composter", dict, Comparer.UnnamedDictComparerSection(
    ("active_time", int, None),
    ("can_work_in_rain", bool, None),
    ("goal_cooldown", int, None),
    ("on_arrival", dict, EntitiesComparerTemplates.event_target_comparer),
    ("priority", int, None),
    ("speed_multiplier", decimal, None),
    ("work_in_rain_tolerance", int, None),
))

comparers = [
    admire_item_comparer,
    avoid_block_comparer,
    avoid_mob_type_comparer,
    barter_comparer,
    beg_comparer,
    breed_comparer,
    celebrate_comparer,
    celebrate_survive_comparer,
    charge_attack_comparer,
    charge_held_item_comparer,
    circle_around_anchor_comparer,
    controlled_by_player_comparer,
    croak_comparer,
    defend_trusted_target_comparer,
    defend_village_target_comparer,
    dig_comparer,
    dragonchargeplayer_comparer,
    dragondeath_comparer,
    dragonflaming_comparer,
    dragonholdingpattern_comparer,
    dragonlanding_comparer,
    dragonscanning_comparer,
    dragonstrafeplayer_comparer,
    dragontakeoff_comparer,
    drink_milk_comparer,
    drink_potion_comparer,
    drop_item_for_comparer,
    eat_carried_item_comparer,
    eat_mob_comparer,
    emerge_comparer,
    enderman_leave_block_comparer,
    enderman_take_block_comparer,
    equip_item_comparer,
    explore_outskirts_behavior,
    fertilize_farm_block_comparer,
    find_cover_comparer,
    find_mount_comparer,
    find_underwater_treasure_comparer,
    fire_at_target_comparer,
    flee_sun_comparer,
    float_comparer,
    float_wander_comparer,
    follow_caravan_comparer,
    follow_mob_comparer,
    follow_owner_comparer,
    follow_parent_comparer,
    follow_target_captain_comparer,
    go_and_give_items_to_noteblock_comparer,
    go_and_give_items_to_owner_comparer,
    go_home_comparer,
    guardian_attack_comparer,
    harvest_farm_block_comparer,
    hide_comparer,
    hold_ground_comparer,
    hurt_by_target_comparer,
    inspect_bookshelf_comparer,
    investigate_suspicious_location_comparer,
    jump_around_target_comparer,
    jump_to_block_comparer,
    knockback_roar,
    lay_down_comparer,
    lay_egg_comparer,
    leap_at_target_comparer,
    look_at_entity_comparer,
    look_at_player_comparer,
    look_at_target,
    look_at_trading_player_comparer,
    make_love_comparer,
    melee_attack_comparer,
    melee_box_attack_comparer,
    mingle_comparer,
    mount_pathing_comparer,
    move_away_from_target,
    move_indoors_comparer,
    move_outdoors_comparer,
    move_to_block_comparer,
    move_to_land_comparer,
    move_to_lava_comparer,
    move_to_liquid_comparer,
    move_to_random_block_comparer,
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
    open_door_comparer,
    owner_hurt_by_target_comparer,
    owner_hurt_target_comparer,
    panic_comparer,
    pet_sleep_with_owner_comparer,
    pickup_items_comparer,
    play_comparer,
    play_dead_comparer,
    player_ride_tamed_comparer,
    raid_garden_comparer,
    ram_attack_comparer,
    random_breach_comparer,
    random_fly_comparer,
    random_hover_comparer,
    random_look_around_comparer,
    random_look_around_and_sit_comparer,
    random_search_and_dig_comparer,
    random_sitting_comparer,
    random_stroll_comparer,
    random_swim_comparer,
    ranged_attack_comparer,
    ravager_blocked_comparer,
    receive_love_comparer,
    restrict_open_door_comparer,
    rise_to_liquid_level,
    roar_comparer,
    roll_comparer,
    run_around_like_crazy_comparer,
    scared_comparer,
    send_event_comparer,
    share_items_comparer,
    silverfish_merge_with_stone_comparer,
    silverfish_wake_up_friends_comparer,
    skeleton_horse_trap_comparer,
    sleep_comparer,
    slime_attack_comparer,
    slime_float_comparer,
    slime_keep_on_jumping_comparer,
    slime_random_direction_comparer,
    snacking_comparer,
    sneeze_comparer,
    sonic_boom_comparer,
    sniff_comparer,
    squid_dive_comparer,
    squid_flee_comparer,
    squid_idle_comparer,
    squid_move_away_from_ground_comparer,
    squid_out_of_water_comparer,
    stalk_and_pounce_on_target_comparer,
    stay_near_noteblock_comparer,
    stay_while_sitting_comparer,
    stomp_attack_comparer,
    stomp_turtle_egg_comparer,
    stroll_towards_village_comparer,
    summon_entity_comparer,
    swell_comparer,
    swim_idle_comparer,
    swim_wander_comparer,
    swim_with_entity_comparer,
    swoop_attack_comparer,
    take_flower_comparer,
    target_when_pushed_comparer,
    tempt_comparer,
    timer_flag_1_comparer,
    timer_flag_2_comparer,
    timer_flag_3_comparer,
    trade_interest_comparer,
    wither_random_attack_pos_goal_comparer,
    wither_target_highest_damage_comparer,
    work_comparer,
    work_composter_comparer,
]
