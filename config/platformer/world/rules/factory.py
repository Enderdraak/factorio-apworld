from rule_builder.rules import Has, Rule

from .classes import CanAutomate, CanCraft, UnlockedRecipe
from .factory_base import get_events_rules as base_get_events_rules, get_locations_rules


# Fuel
can_automate_chemical_fuel = (
    CanAutomate('coal') | CanAutomate('carbon')
        | CanAutomate('solid-fuel') | CanAutomate('rocket-fuel') | CanAutomate('nuclear-fuel')
        | CanAutomate('yumako') | CanAutomate('jellynut') | CanAutomate('yumako-mash') | CanAutomate('jelly')
)


# Power
has_boiler_power = CanCraft('boiler') & CanCraft('steam-engine') & can_automate_chemical_fuel
has_heating_power = CanCraft('heating-tower') & CanCraft('heat-exchanger') & CanCraft('steam-turbine') & can_automate_chemical_fuel
has_nuclear_power = CanCraft('nuclear-reactor') & CanCraft('heat-exchanger') & CanCraft('steam-turbine') & CanAutomate('uranium-fuel-cell')
has_fusion_power = CanCraft('fusion-reactor') & CanCraft('fusion-generator') & CanAutomate('fusion-power-cell')

has_non_solar_power = has_boiler_power | has_heating_power | has_nuclear_power | has_fusion_power


# Enemies
can_destroy_medium_asterorid = CanCraft('gun-turret') & CanAutomate('firearm-magazine') & Has('physical-projectile-damage', 6)
can_destroy_big_asterorid = CanCraft('rocket-turret') & CanAutomate('rocket') & Has('stronger-explosives', 6) & can_destroy_medium_asterorid
can_destroy_huge_asterorid = CanCraft('railgun-turret') & CanAutomate('railgun-ammo') & can_destroy_big_asterorid


# Thrusters
has_truster_and_propellants = (
    CanCraft('thruster')
        & CanAutomate('thruster-fuel') & CanAutomate('thruster-oxidizer')
        # Pipes are needed to transport propellants
        & CanCraft('pipe') & CanCraft('pipe-to-ground')
        # Pumps and storage tanks allow thruster throttling
        & CanCraft('pump') & CanCraft('storage-tank')
)


# Oil stuff
can_crack_oil = CanCraft('chemical-plant') & UnlockedRecipe('heavy-oil-cracking') & UnlockedRecipe('light-oil-cracking')
can_burn_oil = CanCraft('chemical-plant') & UnlockedRecipe('solid-fuel-from-heavy-oil') & UnlockedRecipe('solid-fuel-from-light-oil')


def get_events_rules() -> dict[str, Rule]:
    rules = base_get_events_rules()

    # Advanced oil processing need to have storage tanks to mesure output levels and some way to deal with excess production
    rules['Automate advanced-oil-processing on space-platform'] &= CanCraft('storage-tank') & (can_crack_oil | can_burn_oil)

    # Space location rules
    rules['Reach fulgora with space-platform'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    rules['Reach gleba with space-platform'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    rules['Reach vulcanus with space-platform'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    rules['Reach aquilo with space-platform'] &= can_destroy_big_asterorid & has_truster_and_propellants
    rules['Reach solar-system-edge with space-platform'] &= can_destroy_huge_asterorid & has_truster_and_propellants & has_non_solar_power
    rules['Reach shattered-planet with space-platform'] &= can_destroy_huge_asterorid & has_truster_and_propellants & has_non_solar_power

    return rules
