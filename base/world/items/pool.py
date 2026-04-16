import collections

from ...data.raw import technologies
from ...data.utils import upgrades_levels, upgrades_map
from ...utils import range_inclusive
from .classification import is_progression


# Minimum, maximum and default count that can be added to the pool for each upgrade
upgrades_min_count: dict[str, int] = {}
upgrades_max_count: dict[str, int | None] = {}
upgrades_default_count: dict[str, int] = {}

for name, levels in upgrades_levels.items():
    upgrades_min_count[name] = 0
    for level in range_inclusive(1, len(levels)):
        if is_progression(name, level):
            upgrades_min_count[name] = level

    match levels[-1].max_level:
        case None:
            upgrades_max_count[name] = len(levels)
        case 'infinite':
            upgrades_max_count[name] = None
        case max_level:
            upgrades_max_count[name] = max_level

    if levels[-1].max_level is None:
        upgrades_default_count[name] = len(levels)
    else:
        upgrades_default_count[name] = len(levels) - 1


# Recipe pool
recipe_pool = collections.Counter()

for technology in technologies:
    # Ignore upgrades because it would make things messy
    if technology.name in upgrades_map:
        continue

    for recipe_name in technology.unlocked_recipes:
        recipe_pool[recipe_name] += 1
