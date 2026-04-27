from rule_builder.rules import Rule

from ...data.classes import Surface
from ..rules import CanCraft, UnlockedRecipe
from .factory_base import get_productions as base_get_productions


def get_productions(surface: Surface) -> dict[str, tuple[Rule, dict[str, bool]]]:
    productions = base_get_productions(surface)

    # Advanced oil processing need to have storage tanks to mesure output levels and some way to deal with excess production
    has_chemical_plant = CanCraft('chemical-plant', surface)
    has_storage_tank = CanCraft('storage-tank', surface)

    can_deal_with_excess_heavy_oil = has_chemical_plant & (UnlockedRecipe('heavy-oil-cracking') | UnlockedRecipe('solid-fuel-from-heavy-oil'))
    can_deal_with_excess_light_oil = has_chemical_plant & (UnlockedRecipe('light-oil-cracking') | UnlockedRecipe('solid-fuel-from-light-oil'))

    productions['Automate advanced-oil-processing crafting'] = (
        productions['Automate advanced-oil-processing crafting'][0] & has_storage_tank & can_deal_with_excess_heavy_oil & can_deal_with_excess_light_oil,
        productions['Automate advanced-oil-processing crafting'][1],
    )

    return productions
