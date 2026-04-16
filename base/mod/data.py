from ..data.raw import science_packs, technologies
from ..data.utils import upgrades_map, upgrades_levels
from ..world import FactorioWorld

def get_mod_name(world: FactorioWorld) -> str:
    return f'AP-{world.multiworld.seed_name}-P{world.player}-{world.multiworld.get_file_safe_player_name(world.player)}'


def get_mod_version(world: FactorioWorld) -> str:
    return '.'.join(map(str, world.world_version))


def get_location_data(world, location) -> dict:
    return (location.data, {
        'name': location.item.name if world.options.tech_tree_information.value == 2 else None,
        'player_name': world.multiworld.player_name[location.item.player] if world.options.tech_tree_information.value == 2 else None,
        'advancement': location.item.advancement if world.options.tech_tree_information.value else None,
        'useful': location.item.useful if world.options.tech_tree_information.value else None,
        'trap': location.item.trap if world.options.tech_tree_information.value else None,
    })


def get_mod_data(world: FactorioWorld) -> dict:
    free_sample_blacklist = {}
    free_sample_blacklist.update({item: 1 for item in science_packs})
    free_sample_blacklist.update({item: 1 for item in world.options.free_sample_blacklist.value})
    free_sample_blacklist.update({item: 0 for item in world.options.free_sample_whitelist.value})

    progressive_items = {}
    progressive_items.update({ name: [level.name for level in levels] for name, levels in upgrades_levels.items() })
    progressive_items.update(world.progressive_items)

    return {
        'custom_recipes': {},
        'data_utils': {
            'upgrades_map': upgrades_map,
        },
        'energy_link': 0,
        'evolution_trap_increase': 10,
        'free_samples': world.options.free_samples.value,
        'free_sample_blacklist': free_sample_blacklist,
        'free_sample_quality_name': world.options.free_samples_quality.current_key,
        'locations': [get_location_data(world, location) for location in world.get_locations() if not location.is_event],
        'max_science_pack': world.options.max_science_pack.value,
        'mod_name': get_mod_name(world),
        'options': {
            'split_technologies': world.options.split_technologies.value,
        },
        'progressive_items': progressive_items,
        'seed_name': world.multiworld.seed_name,
        'slot_name': world.player_name,
        'slot_player': world.player,
        'starting_items': world.options.starting_items.value,
        'tech_tree_information': world.options.tech_tree_information.value,
        'technologies': [technology.name for technology in technologies],
        'victory_condition': world.options.goal.get_victory_condition(),
        'world_gen': world.options.world_gen.value,
    }
