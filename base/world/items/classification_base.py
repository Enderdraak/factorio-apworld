from ...data.raw import technologies
from ...data.utils import upgrades_levels, upgrades_map


def _has_advancement_modifier(technology) -> bool:
    return any((
        len(technology.unlocked_recipes) > 0,
        len(technology.unlocked_space_locations) > 0,
        'mining-with-fluid' in technology.modifiers,
    ))


def is_advancement(name: str, index: int = 0, split_technologies: bool | None = None) -> bool:
    """
    Is the given item advancement.
    index represent the item index (equivalent to how many of that item is already in the pool)
    """

    assert index >= 0, 'Invalid index'

    if name in upgrades_levels:
        if index < len(upgrades_levels[name]):
            return any((
                _has_advancement_modifier(upgrades_levels[name][index_to_check])
                for index_to_check in range(index, len(upgrades_levels[name]))
            ))
        else:
            return False
    elif name.startswith('quality: '):
        return False
    elif name.startswith('recipe: '):
        return index == 0
    elif name.startswith('space location: '):
        return index == 0
    else:
        if split_technologies:
            return False
        else:
            return _has_advancement_modifier(technologies[name])


def is_useful(name: str, index: int = 0, split_technologies: bool | None = None) -> bool:
    """
    Is the given item useful.
    index represent the item index (equivalent to how many of that item is already in the pool)
    """

    assert index >= 0, 'Invalid index'

    if name in upgrades_levels:
        if index < len(upgrades_levels[name]):
            return any((
                upgrades_levels[name][index_to_check].has_modifier
                for index_to_check in range(index, len(upgrades_levels[name]))
            ))
        else:
            return upgrades_levels[name][-1].has_modifier
    elif name.startswith('quality: '):
        return True
    elif name.startswith('recipe: '):
        return True
    elif name.startswith('space location: '):
        return True
    else:
        return technologies[name].has_modifier
