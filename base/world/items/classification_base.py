from ...data.raw import technologies
from ...data.utils import upgrades_levels, upgrades_map


def is_progression(name: str, level: int | None = None, split_technologies: bool | None = None) -> bool:
    if name in upgrades_levels:
        assert level is not None and level > 0, f'Invalid level: {level}'

        if level > len(upgrades_levels[name]):
            return False

        return upgrades_levels[name][level-1].has_unlock
    else:
        assert level is None, f'Invalid level: {level}'

        if len(technologies[name].unlocked_space_locations) > 0:
            return True

        if not split_technologies and len(technologies[name].unlocked_recipes) > 0:
            return True

        return False


def is_usefull(name: str, level: int | None = None, split_technologies: bool | None = None) -> bool:
    if name in upgrades_levels:
        assert level is not None and level > 0, f'Invalid level: {level}'

        if level > len(upgrades_levels[name]):
            return upgrades_levels[name][-1].has_modifier

        return upgrades_levels[name][level-1].has_modifier
    else:
        assert level is None, f'Invalid level: {level}'

        return technologies[name].has_modifier
