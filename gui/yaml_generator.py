"""
Generate a SkywardSwordHD.yaml file from the current randomizer config
and Archipelago settings.

This combines the sshd-rando config.yaml settings with the AP-specific
settings (death link, cheats, etc.) into a single YAML template that
Archipelago can consume directly.
"""

from pathlib import Path

import yaml

from logic.config import Config
from logic.settings import Setting

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gui.archipelago import Archipelago

# Maps sshd-rando setting names to YAML keys where they differ.
# Most are 1:1 so they don't need to be in this map.
_RANDO_TO_YAML = {
    "small_key_shuffle": "small_key_shuffle",
    "boss_key_shuffle": "boss_key_shuffle",
    "map_shuffle": "map_shuffle",
    "skip_g3": "skip_ghirahim3",
}

# Settings that use on/off in sshd-rando but true/false in the YAML
_BOOL_SETTINGS = {
    "gratitude_crystal_shuffle", "stamina_fruit_shuffle", "npc_closet_shuffle",
    "hidden_item_shuffle", "goddess_chest_shuffle", "tadtone_shuffle",
    "gossip_stone_treasure_shuffle", "randomize_dungeons", "randomize_trials",
    "randomize_door_entrances", "decouple_double_doors",
    "randomize_interior_entrances", "randomize_overworld_entrances",
    "decouple_entrances", "decouple_skykeep_layout",
    "random_starting_statues", "limit_starting_spawn",
    "burn_traps", "curse_traps", "noise_traps", "groose_traps", "health_traps",
    "open_thunderhead", "open_batreaux_shed", "skip_harp_playing", "skip_misc_cutscenes",
    "no_spoiler_log", "enable_back_in_time", "underground_rupee_shuffle",
    "random_bottle_contents", "randomize_shop_prices",
    "full_wallet_upgrades", "random_trial_object_positions",
    "upgraded_skyward_strike", "faster_air_meter_depletion",
    "unlock_all_groosenator_destinations", "allow_flying_at_night",
    "natural_night_connections", "dungeons_include_sky_keep",
    "empty_unrequired_dungeons", "small_keys_in_fancy_chests",
    "cutoff_game_over_music", "spawn_hearts",
    "skip_horde", "skip_g3", "skip_demise",
    "tunic_swap", "lightning_skyward_strike", "starry_skies", "remove_enemy_music",
    "start_with_all_bugs", "start_with_all_treasures",
    # Logic tricks
    "logic_early_lake_floria", "logic_beedles_island_cage_chest_dive",
    "logic_volcanic_island_dive", "logic_east_island_dive",
    "logic_advanced_lizalfos_combat", "logic_long_ranged_skyward_strikes",
    "logic_gravestone_jump", "logic_waterfall_cave_jump",
    "logic_bird_nest_item_from_beedles_shop", "logic_beedles_shop_with_bombs",
    "logic_stuttersprint", "logic_precise_beetle", "logic_bomb_throws",
    "logic_faron_woods_with_groosenator", "logic_itemless_first_timeshift_stone",
    "logic_stamina_potion_through_sink_sand", "logic_brakeslide",
    "logic_lanayru_mine_quick_bomb", "logic_tot_skip_brakeslide",
    "logic_tot_slingshot", "logic_fire_node_without_hook_beetle",
    "logic_cactus_bomb_whip", "logic_skippers_fast_clawshots",
    "logic_skyview_spider_roll", "logic_skyview_coiled_rupee_jump",
    "logic_skyview_precise_slingshot", "logic_et_keese_skyward_strike",
    "logic_et_slope_stuttersprint", "logic_et_bombless_scaldera",
    "logic_lmf_whip_switch", "logic_lmf_ceiling_precise_slingshot",
    "logic_lmf_whip_armos_room_timeshift_stone", "logic_lmf_minecart_jump",
    "logic_lmf_bellowsless_moldarach", "logic_ac_lever_jump_trick",
    "logic_ac_chest_after_whip_hooks_jump", "logic_sandship_jump_to_stern",
    "logic_sandship_itemless_spume", "logic_sandship_no_combination_hint",
    "logic_fs_pillar_jump", "logic_fs_practice_sword_ghirahim_2",
    "logic_present_bow_switches", "logic_skykeep_vineclip",
    # Shortcuts
    "shortcut_ios_bridge_complete", "shortcut_spiral_log_to_btt",
    "shortcut_logs_near_machi", "shortcut_faron_log_to_floria",
    "shortcut_deep_woods_log_before_tightrope", "shortcut_deep_woods_log_before_temple",
    "shortcut_eldin_entrance_boulder", "shortcut_eldin_ascent_boulder",
    "shortcut_vs_flames", "shortcut_lanayru_bars", "shortcut_west_wall_minecart",
    "shortcut_sand_oasis_minecart", "shortcut_minecart_before_caves",
    "shortcut_skyview_boards", "shortcut_skyview_bars",
    "shortcut_earth_temple_bridge", "shortcut_lmf_wind_gates",
    "shortcut_lmf_boxes", "shortcut_lmf_bars_to_west_side",
    "shortcut_ac_bridge", "shortcut_ac_water_vents",
    "shortcut_sandship_windows", "shortcut_sandship_brig_bars",
    "shortcut_fs_outside_bars", "shortcut_fs_lava_flow",
    "shortcut_sky_keep_svt_room_bars", "shortcut_sky_keep_fs_room_lower_bars",
    "shortcut_sky_keep_fs_room_upper_bars",
}

# Integer settings (value stored as string in sshd-rando)
_INT_SETTINGS = {
    "required_dungeon_count", "starting_tablets", "random_starting_item_count",
    "trial_treasure_shuffle", "starting_hearts", "peatrice_conversations",
}

# Settings that use "progressive_items" → "true"/"false" 
_PROGRESSIVE_BOOL = {"progressive_items"}


def _convert_setting_value(name: str, setting: Setting):
    """Convert a sshd-rando Setting to the appropriate YAML value."""
    val = setting.value

    if name in _BOOL_SETTINGS:
        if val == "on":
            return True
        elif val == "off":
            return False
        # Already bool-like string
        return val in ("true", "True", True)

    if name in _PROGRESSIVE_BOOL:
        return val == "on"

    if name in _INT_SETTINGS:
        try:
            return int(val)
        except (ValueError, TypeError):
            return val

    return val


def generate_yaml(
    config: Config,
    ap_settings: dict,
    output_path: Path,
) -> Path:
    """
    Build and write a SkywardSwordHD.yaml from the current config and AP settings.

    Args:
        config: The sshd-rando Config object (with all randomizer settings).
        ap_settings: Dict of Archipelago-specific settings from the AP tab.
        output_path: Where to write the YAML file.

    Returns:
        The Path of the written YAML file.
    """
    player_name = ap_settings.get("player_name", "Player1")

    out: dict = {}
    out["name"] = player_name
    out["description"] = f"Skyward Sword HD Archipelago YAML for {player_name}"
    out["game"] = "Skyward Sword HD"
    out["requires"] = {
        "version": "0.6.6",
        "game": {"Skyward Sword HD": "0.7.2"},
    }

    game_settings: dict = {}

    # ── Extract path ──────────────────────────────────────────────────
    game_settings["extract_path"] = ap_settings.get("extract_path", "")

    # ── Archipelago options ───────────────────────────────────────────
    game_settings["death_link"] = ap_settings.get("death_link", False)
    game_settings["breath_link"] = ap_settings.get("breath_link", False)
    game_settings["progression_balancing"] = ap_settings.get("progression_balancing", 50)
    game_settings["use_alternative_logo"] = ap_settings.get("use_alternative_logo", False)
    game_settings["archipelago_item_model"] = ap_settings.get("archipelago_item_model", 2)

    # ── Cheats ────────────────────────────────────────────────────────
    cheat_keys = [k for k in ap_settings if k.startswith("cheat_")]
    for key in cheat_keys:
        game_settings[key] = ap_settings[key]

    # ── Config method: leave config_yaml_path and setting_string blank ─
    game_settings["config_yaml_path"] = ""
    game_settings["setting_string"] = ""
    game_settings["sshdr_seed"] = config.seed

    # ── Randomizer settings ───────────────────────────────────────────
    if config.settings:
        setting_map = config.settings[0]

        for setting_name, setting in setting_map.settings.items():
            yaml_key = _RANDO_TO_YAML.get(setting_name, setting_name)
            game_settings[yaml_key] = _convert_setting_value(setting_name, setting)

        # Starting inventory
        starting_items = {}
        for item in setting_map.starting_inventory.elements():
            starting_items[item] = starting_items.get(item, 0) + 1
        game_settings["custom_starting_items"] = starting_items if starting_items else {}

        # No-spoiler-log is derived from generate_spoiler_log
        game_settings["no_spoiler_log"] = not config.generate_spoiler_log

    out["Skyward Sword HD"] = game_settings

    # ── Write ─────────────────────────────────────────────────────────
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        # Write with nice formatting
        yaml.dump(out, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return output_path
