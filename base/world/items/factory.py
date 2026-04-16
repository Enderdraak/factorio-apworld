from BaseClasses import ItemClassification

from ...data.raw import technologies
from ...data.utils import upgrades_levels, upgrades_map
from ...utils import range_inclusive
from ..options import FactorioOptions
from .classes import FactorioItem, FactorioRecipeItem, FactorioTechnologyItem
from .classification import is_progression, is_usefull
from .pool import recipe_pool


def create_item(options: FactorioOptions, progressive_levels: dict[str, list[str]], player: int, item_name: str) -> FactorioItem:
    if item_name in upgrades_levels:
        name = item_name
        level = len(upgrades_levels[item_name])
    elif item_name in progressive_levels:
        name = progressive_levels[item_name][-1]
        level = None
    else:
        name = item_name
        level = None

    if is_progression(name, level, options.split_technologies):
        classification = ItemClassification.progression
    elif is_usefull(name, level, options.split_technologies):
        classification = ItemClassification.useful
    else:
        classification = ItemClassification.filler

    return FactorioItem(item_name, classification, player)


def create_items(options: FactorioOptions, progressive_levels: dict[str, list[str]], player: int) -> list[FactorioItem]:
    # Build reverse progressive lookup map
    progressive_map: dict[str, str] = {}
    for name, levels in progressive_levels.items():
        for level in levels:
            progressive_map[level] = name

    items = []

    for technology in technologies:
        if technology.name in upgrades_map:
            continue

        if options.split_technologies:
            if len(technology.unlocked_space_locations) == 0 and len(technology.modifiers) == 0:
                continue

        if technology.name in progressive_map:
            item_name = progressive_map[technology.name]
            index = progressive_levels[item_name].index(technology.name)
            technologies_to_check = progressive_levels[item_name][index:]
        else:
            item_name = technology.name
            technologies_to_check = [technology.name]

        if any((is_progression(technology_to_check, None, options.split_technologies) for technology_to_check in technologies_to_check)):
            classification = ItemClassification.progression
        elif any((is_usefull(technology_to_check, None, options.split_technologies) for technology_to_check in technologies_to_check)):
            classification = ItemClassification.useful
        else:
            classification = ItemClassification.filler

        items.append(FactorioTechnologyItem(item_name, classification, player))

    for item_name, levels in upgrades_levels.items():
        count = options.upgrades_count[item_name]

        for level in range_inclusive(1, count):
            if any((is_progression(item_name, level_to_check, options.split_technologies) for level_to_check in range_inclusive(level, count))):
                classification = ItemClassification.progression
            elif any((is_usefull(item_name, level_to_check, options.split_technologies) for level_to_check in range_inclusive(level, count))):
                classification = ItemClassification.useful
            else:
                classification = ItemClassification.filler

            items.append(FactorioTechnologyItem(item_name, classification, player))

    if options.split_technologies:
        for recipe_name in recipe_pool.elements():
            if f'{recipe_name} recipe' in progressive_map:
                items.append(FactorioItem(progressive_map[f'{recipe_name} recipe'], ItemClassification.progression, player))
            else:
                items.append(FactorioRecipeItem(recipe_name, player))

    assert len(items) == get_item_count(options), 'Unexpected item count'

    return items


def get_item_count(options: FactorioOptions) -> int:
    count = 0

    for technology in technologies:
        if technology.name in upgrades_map:
            continue

        if options.split_technologies:
            if len(technology.unlocked_space_locations) == 0 and len(technology.modifiers) == 0:
                continue

        count += 1

    for item_name in upgrades_levels.keys():
        count += options.upgrades_count[item_name]

    if options.split_technologies:
        count += recipe_pool.total()

    return count
