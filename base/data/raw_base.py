import importlib.resources
import json

from .classes import Machine, Recipe, SpaceLocation, Surface, SurfaceCondition, Table, Technology


data = json.loads(importlib.resources.files(__name__).parent.joinpath('data.json').read_text())

def get_data(type: str):
    return ((k, v) for k, v in data.get(type, {}).items() if not v.get('hidden', False) and not v.get('parameter', False))


# Surfaces
surfaces = Table()
surfaces_accessible_at_start = {'nauvis'}

for surface_name, surface_data in get_data('surface'):
    surfaces.add(Surface(surface_name, surface_data['surface_properties']))

for planet_name, planet_data in get_data('planet'):
    surfaces.add(Surface(planet_name, planet_data['surface_properties']))


# Space locations
_asteroid_to_chunks = {}
_asteroid_to_asteroid = {}

for asteroid_name, asteroid_data in get_data('asteroid'):
    for dying_trigger_effect in asteroid_data.get('dying_trigger_effect', []):
        if dying_trigger_effect['type'] == 'create-asteroid-chunk':
            if not asteroid_name in _asteroid_to_chunks:
                _asteroid_to_chunks[asteroid_name] = list()

            _asteroid_to_chunks[asteroid_name].append(dying_trigger_effect['asteroid_name'])

        if dying_trigger_effect['type'] == 'create-entity':
            if not asteroid_name in _asteroid_to_asteroid:
                _asteroid_to_asteroid[asteroid_name] = list()

            _asteroid_to_asteroid[asteroid_name].append(dying_trigger_effect['entity_name'])

def _recursive_asteroid_to_chunks(asteroid_name: str):
    asteroid_chunks = set(_asteroid_to_chunks.get(asteroid_name, []))

    for asteroid_name in _asteroid_to_asteroid.get(asteroid_name, []):
        asteroid_chunks.update(_recursive_asteroid_to_chunks(asteroid_name))

    return asteroid_chunks

space_locations = Table()

for space_location_name, space_location_data in [*get_data('space-location'), *get_data('planet')]:
    asteroid_chunks = set()

    for asteroid_spawn_definition in space_location_data.get('asteroid_spawn_definitions', []):
        if asteroid_spawn_definition.get('type', 'entity') == 'asteroid-chunk':
            asteroid_chunks.add(asteroid_spawn_definition['asteroid'])
        else:
            asteroid_chunks.update(_recursive_asteroid_to_chunks(asteroid_spawn_definition['asteroid']))

    space_locations.add(SpaceLocation(
        name=space_location_name,
        asteroid_chunks=asteroid_chunks,
        unlocked_at_start=space_location_name == 'nauvis',
        accessible_at_start=space_location_name == 'nauvis',
    ))

for space_connection_name, space_connection_data in get_data('space-connection'):
    space_locations[space_connection_data['from']].connections.add(space_connection_data['to'])
    space_locations[space_connection_data['to']].connections.add(space_connection_data['from'])


# Machines
machines = Table()

for machine_name, machine_data in get_data("assembling-machine"):
    machines.add(Machine(
        machine_name,
        set(machine_data["crafting_categories"]),
        [SurfaceCondition.from_data(surface_condition) for surface_condition in machine_data.get('surface_conditions', [])],
    ))

for machine_name, machine_data in get_data("asteroid-collector"):
    machines.add(Machine(
        machine_name,
        {'asteroid-chunk'},
        [SurfaceCondition.from_data(surface_condition) for surface_condition in machine_data.get('surface_conditions', [])],
    ))

for machine_name, machine_data in get_data("character"):
    machines.add(Machine(machine_name, set(machine_data["crafting_categories"])))

for machine_name, machine_data in get_data("mining-drill"):
    machines.add(Machine(machine_name, set(machine_data["resource_categories"])))

for machine_name, machine_data in get_data("furnace"):
    machines.add(Machine(machine_name, set(machine_data["crafting_categories"])))

for machine_name, machine_data in get_data("rocket-silo"):
    machines.add(Machine(machine_name, set(machine_data["crafting_categories"])))

machines_available_at_start = {'character'}


# Recipes
recipes = Table()
recipes_unlocked_at_start: dict[str] = set()
recipes_mining_with_fluid: dict[str] = set()

for asteroid_chunk_name, asteroid_chunk_data in get_data('asteroid-chunk'):
    if not 'minable' in asteroid_chunk_data:
        continue

    recipes.add(Recipe(asteroid_chunk_name, 'asteroid-chunk', {}, {asteroid_chunk_data['minable']['result']: 1}, 0))
    recipes_unlocked_at_start.add(asteroid_chunk_name)

for recipe_name, recipe_data in get_data('recipe'):
    recipe = Recipe(
        recipe_name,
        recipe_data.get("category", "crafting"),
        {ingredient["name"]: ingredient["amount"] for ingredient in recipe_data.get("ingredients", [])},
        {result["name"]: (result["amount"] if "amount" in result else (result["amount_min"] + result["amount_max"]) / 2) * result.get('probability', 1) + result.get('extra_count_fraction', 0) for result in recipe_data.get("results", [])},
        recipe_data.get("energy_required", 0.5)
    )

    recipes.add(recipe)
    if recipe_data.get("enabled", True):
        recipes_unlocked_at_start.add(recipe.name)

for resource_name, resource_data in get_data("resource"):
    if "result" in resource_data["minable"]:
        products = {resource_data["minable"]["result"]: 1}
    elif "results" in resource_data["minable"]:
        products = {result_data["name"]: 1 for result_data in resource_data["minable"]["results"]}
    else:
        continue

    recipe = Recipe(
        f"mining-{resource_name}",
        resource_data.get("category", "basic-solid"),
        {resource_data["minable"]["required_fluid"]: resource_data["minable"]["fluid_amount"]} if "required_fluid" in resource_data["minable"] else {},
        products,
        resource_data["minable"]["mining_time"]
    )

    recipes.add(recipe)
    recipes_unlocked_at_start.add(recipe.name)

    if "required_fluid" in resource_data["minable"]:
        recipes_mining_with_fluid.add(recipe.name)


# Science packs
# this is a list because keeping the order in which they are defined is important
science_packs = list()

for tool_name, tool_data in get_data('tool'):
    if tool_data['subgroup'] == 'science-pack':
        science_packs.append(tool_name)


# Technologies
technologies = Table()

for technology_name, technology_data in get_data('technology'):
    technology = Technology(technology_name)

    for effect in technology_data.get('effects', []):
        match effect["type"]:
            case "unlock-recipe":
                technology.unlocked_recipes.add(effect["recipe"])
            case "mining-with-fluid":
                technology.unlocked_recipes.update(recipes_mining_with_fluid)
            case 'unlock-space-location':
                technology.unlocked_space_locations.add(effect['space_location'])
            case _:
                technology.modifiers.append(effect["type"])

    technology.upgrade = technology_data.get('upgrade', False)
    technology.max_level = technology_data.get('max_level')

    unit = technology_data.get('unit')
    if unit is not None:
        technology.unit_count = unit.get('count')

    technologies.add(technology)


# Items
_item_types = [
    'item',
    'ammo',
    'capsule',
    'gun',
    'item-with-entity-data',
    'item-with-label',
    'item-with-inventory',
    'blueprint-book',
    'item-with-tags',
    'selection-tool',
    'blueprint',
    'copy-paste-tool',
    'deconstruction-item',
    'spidertron-remote',
    'upgrade-item',
    'module',
    'rail-planner',
    'space-platform-starter-pack',
    'tool',
    'armor',
    'repair-tool',
]

items = set()

for item_type in _item_types:
    for item_name, item_data in get_data(item_type):
        items.add(item_name)


# Cleanup
del recipes_mining_with_fluid
