from rule_builder.rules import Rule

from ...data.classes import Surface
from .asteroid import get_asteroid_productions
from .crafting import get_crafting_productions
from .mining import get_mining_productions

def get_productions(surface: Surface) -> dict[str, tuple[Rule, dict[str, bool]]]:
    productions = {}

    productions.update(get_asteroid_productions(surface))
    productions.update(get_crafting_productions(surface))
    productions.update(get_mining_productions(surface))

    return productions
