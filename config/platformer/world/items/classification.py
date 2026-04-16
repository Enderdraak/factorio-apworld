from .classification_base import is_progression as base_is_progression, is_usefull


def is_progression(name: str, level: int | None = None, split_technologies = None) -> bool:
    if name == 'physical-projectile-damage' and level <= 6:
        return True

    if name == 'stronger-explosives' and level <= 6:
        return True

    return base_is_progression(name, level, split_technologies)
