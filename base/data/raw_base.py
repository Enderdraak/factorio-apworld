from collections import defaultdict
from collections.abc import Iterable
from importlib import resources
from json import loads as json_loads

from .classes import Machine, Recipe, SpaceLocation, Surface, SurfaceCondition, Table, Technology


# Raw data
types = {
    'assembling-machine': { 'children': ['rocket-silo'] },
    'crafting-machine': { 'abstract': True, 'children': ['assembling-machine', 'furnace'] },
    'entity': { 'abstract': True, 'children': ['cliff', 'entity-with-health', 'resource'] }, # Incomplete list
    'entity-with-health': { 'abstract': True, 'children': ['entity-with-owner', 'fish', 'simple-entity', 'tree'] }, # Incomplete list
    'entity-with-owner': { 'abstract': True, 'children': ['lightning-attractor'] }, # Incomplete list
    'item': { 'children': ['ammo', 'capsule', 'gun', 'item-with-entity-data', 'item-with-label', 'module', 'rail-planner', 'space-platform-starter-pack', 'tool'] },
    'item-with-inventory': { 'children': ['blueprint-book'] },
    'item-with-label': { 'children': ['item-with-inventory', 'item-with-tags', 'selection-tool'] },
    'selection-tool': { 'children': ['blueprint', 'copy-paste-tool', 'deconstruction-item', 'spidertron-remote', 'upgrade-item'] },
    'space-location': { 'children': ['planet'] },
    'tool': { 'children': ['armor', 'repair-tool'] },
    'tree': { 'children': ['plant'] },
}

data = json_loads(resources.files(__name__).parent.joinpath('data.json').read_text())

def get_prototypes(type: str) -> Iterable[dict]:
    if not types.get(type, {}).get('abstract', False):
        for value in data.get(type, {}).values():
             if not value.get('hidden', False) and not value.get('parameter', False):
                yield value
    for child_type in types.get(type, {}).get('children', []):
        yield from get_prototypes(child_type)

def get_prototype(type: str, name: str) -> dict|None:
    if not types.get(type, {}).get('abstract', False):
        if (prototype := data.get(type, {}).get(name)):
            return prototype
    for child_type in types.get(type, {}).get('children', []):
        if (prototype := get_prototype(child_type, name)):
            return prototype
    return None


# Surfaces
surfaces = Table()
surfaces_accessible_at_start = {'nauvis'}

for prototype in get_prototypes('surface'):
    surfaces.add(Surface(prototype['name'], prototype['surface_properties']))

for prototype in get_prototypes('planet'):
    surfaces.add(Surface(prototype['name'], prototype['surface_properties']))


# Space locations
_asteroid_to_chunks = defaultdict(list)
_asteroid_to_asteroid = defaultdict(list)

for prototype in get_prototypes('asteroid'):
    for dying_trigger_effect in prototype.get('dying_trigger_effect', []):
        if dying_trigger_effect['type'] == 'create-asteroid-chunk':
            _asteroid_to_chunks[prototype['name']].append(dying_trigger_effect['asteroid_name'])

        if dying_trigger_effect['type'] == 'create-entity':
            _asteroid_to_asteroid[prototype['name']].append(dying_trigger_effect['entity_name'])

def _recursive_asteroid_to_chunks(asteroid_name: str):
    asteroid_chunks = set(_asteroid_to_chunks.get(asteroid_name, []))

    for asteroid_name in _asteroid_to_asteroid.get(asteroid_name, []):
        asteroid_chunks.update(_recursive_asteroid_to_chunks(asteroid_name))

    return asteroid_chunks

space_locations = Table()

for prototype in get_prototypes('space-location'):
    asteroid_chunks = set()

    for asteroid_spawn_definition in prototype.get('asteroid_spawn_definitions', []):
        if asteroid_spawn_definition.get('type', 'entity') == 'asteroid-chunk':
            asteroid_chunks.add(asteroid_spawn_definition['asteroid'])
        else:
            asteroid_chunks.update(_recursive_asteroid_to_chunks(asteroid_spawn_definition['asteroid']))

    space_locations.add(SpaceLocation(
        name=prototype['name'],
        asteroid_chunks=asteroid_chunks,
        unlocked_at_start=prototype['name'] == 'nauvis',
        accessible_at_start=prototype['name'] == 'nauvis',
    ))

for prototype in get_prototypes('space-connection'):
    space_locations[prototype['from']].connections.add(prototype['to'])
    space_locations[prototype['to']].connections.add(prototype['from'])


# Machines
machines = Table()

for prototype in get_prototypes('assembling-machine'):
    machines.add(Machine(
        prototype['name'],
        set(prototype['crafting_categories']),
        [SurfaceCondition.from_data(surface_condition) for surface_condition in prototype.get('surface_conditions', [])],
    ))

for prototype in get_prototypes('asteroid-collector'):
    machines.add(Machine(
        prototype['name'],
        {'asteroid-chunk'},
        [SurfaceCondition.from_data(surface_condition) for surface_condition in prototype.get('surface_conditions', [])],
    ))

for prototype in get_prototypes('character'):
    machines.add(Machine(prototype['name'], set(prototype['crafting_categories'])))

for prototype in get_prototypes('mining-drill'):
    machines.add(Machine(prototype['name'], set(prototype['resource_categories'])))

for prototype in get_prototypes('furnace'):
    machines.add(Machine(prototype['name'], set(prototype['crafting_categories'])))

for prototype in get_prototypes('rocket-silo'):
    machines.add(Machine(prototype['name'], set(prototype['crafting_categories'])))

machines_available_at_start = {'character'}


# Recipes
recipes = Table()
recipes_unlocked_at_start: dict[str] = set()
recipes_mining_with_fluid: dict[str] = set()

for prototype in get_prototypes('asteroid-chunk'):
    if not 'minable' in prototype:
        continue

    recipes.add(Recipe(prototype['name'], 'asteroid-chunk', {}, {prototype['minable']['result']: 1}, 0))
    recipes_unlocked_at_start.add(prototype['name'])

for prototype in get_prototypes('recipe'):
    recipe = Recipe(
        prototype['name'],
        prototype.get('category', 'crafting'),
        {ingredient['name']: ingredient['amount'] for ingredient in prototype.get('ingredients', [])},
        {result['name']: (result['amount'] if 'amount' in result else (result['amount_min'] + result['amount_max']) / 2) * result.get('probability', 1) + result.get('extra_count_fraction', 0) for result in prototype.get('results', [])},
        prototype.get("energy_required", 0.5)
    )

    recipes.add(recipe)
    if prototype.get('enabled', True):
        recipes_unlocked_at_start.add(prototype['name'])

for prototype in get_prototypes('resource'):
    if 'result' in prototype['minable']:
        products = {prototype['minable']['result']: 1}
    elif 'results' in prototype['minable']:
        products = {result_data['name']: 1 for result_data in prototype['minable']['results']}
    else:
        continue

    recipe = Recipe(
        f'mining-{prototype['name']}',
        prototype.get('category', 'basic-solid'),
        {prototype['minable']['required_fluid']: prototype['minable']['fluid_amount']} if 'required_fluid' in prototype['minable'] else {},
        products,
        prototype['minable']['mining_time'],
    )

    recipes.add(recipe)
    recipes_unlocked_at_start.add(recipe.name)

    if 'required_fluid' in prototype['minable']:
        recipes_mining_with_fluid.add(recipe.name)


# Science packs
# this is a list because keeping the order in which they are defined is important
science_packs = list()

for prototype in get_prototypes('tool'):
    if prototype['subgroup'] == 'science-pack':
        science_packs.append(prototype['name'])


# Technologies
technologies = Table()

for prototype in get_prototypes('technology'):
    technology = Technology(prototype['name'])

    for effect in prototype.get('effects', []):
        match effect['type']:
            case 'unlock-quality':
                technology.unlocked_qualities.add(effect['quality'])
            case 'unlock-recipe':
                technology.unlocked_recipes.add(effect['recipe'])
            case 'mining-with-fluid':
                technology.unlocked_recipes.update(recipes_mining_with_fluid)
            case 'unlock-space-location':
                technology.unlocked_space_locations.add(effect['space_location'])
            case _:
                technology.modifiers.append(effect['type'])

    technology.upgrade = prototype.get('upgrade', False)
    technology.max_level = prototype.get('max_level')

    if (unit := prototype.get('unit')) is not None:
        technology.unit_count = unit.get('count')

    technologies.add(technology)


# Items
items = set()

for prototype in get_prototypes('item'):
    if 'only-in-cursor' in prototype.get('flags', []):
        continue
    items.add(prototype['name'])


# Cleanup
del recipes_mining_with_fluid
