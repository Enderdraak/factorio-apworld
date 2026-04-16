import itertools

from ...config import progressive_items_with_split_technologies, progressive_items_without_split_technologies
from ...data.raw import technologies
from ...data.utils import upgrades_map
from .pool import recipe_pool


# Generate ids
item_ids = {}

ids = itertools.count(start=1)

for technology in technologies:
    if technology.name in upgrades_map:
        if upgrades_map[technology.name] in item_ids:
            continue
        item_ids[upgrades_map[technology.name]] = next(ids)
    else:
        item_ids[technology.name] = next(ids)

for recipe_name in recipe_pool:
    item_ids[f'{recipe_name} recipe'] = next(ids)

item_ids['progressive science-pack'] = next(ids)
for progressive_name in progressive_items_with_split_technologies:
    if not progressive_name in item_ids:
        item_ids[progressive_name] = next(ids)

    assert all((item in item_ids for item in progressive_items_with_split_technologies[progressive_name])), f'{progressive_name} has invalid items'
for progressive_name in progressive_items_without_split_technologies:
    if not progressive_name in item_ids:
        item_ids[progressive_name] = next(ids)

    assert all((item in item_ids for item in progressive_items_without_split_technologies[progressive_name])), f'{progressive_name} has invalid items'

del ids
