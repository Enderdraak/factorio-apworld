from rule_builder.rules import Has, Rule

from ...data.classes import Surface
from ..rules import CanAutomate, CanCraft
from .factory_base import get_events as base_get_events

def get_events(surface: Surface) -> dict[str, Rule]:
    # Fuel
    can_automate_chemical_fuel = (
        CanAutomate('coal', surface) | CanAutomate('carbon', surface)
            | CanAutomate('solid-fuel', surface) | CanAutomate('rocket-fuel', surface) | CanAutomate('nuclear-fuel', surface)
            | CanAutomate('yumako', surface) | CanAutomate('jellynut', surface) | CanAutomate('yumako-mash', surface) | CanAutomate('jelly', surface)
    )

    # Power
    has_boiler_power = CanCraft('boiler', surface) & CanCraft('steam-engine', surface) & can_automate_chemical_fuel
    has_heating_power = CanCraft('heating-tower', surface) & CanCraft('heat-exchanger', surface) & CanCraft('steam-turbine', surface) & can_automate_chemical_fuel
    has_nuclear_power = CanCraft('nuclear-reactor', surface) & CanCraft('heat-exchanger', surface) & CanCraft('steam-turbine', surface) & CanAutomate('uranium-fuel-cell', surface)
    has_fusion_power = CanCraft('fusion-reactor', surface) & CanCraft('fusion-generator', surface) & CanAutomate('fusion-power-cell', surface)

    has_non_solar_power = has_boiler_power | has_heating_power | has_nuclear_power | has_fusion_power

    # Enemies
    can_destroy_medium_asterorid = CanCraft('gun-turret', surface) & CanAutomate('firearm-magazine', surface) & Has('physical-projectile-damage', 6)
    can_destroy_big_asterorid = CanCraft('rocket-turret', surface) & CanAutomate('rocket', surface) & Has('stronger-explosives', 6) & can_destroy_medium_asterorid
    can_destroy_huge_asterorid = CanCraft('railgun-turret', surface) & CanAutomate('railgun-ammo', surface) & can_destroy_big_asterorid

    # Thrusters
    has_truster_and_propellants = (
        CanCraft('thruster', surface)
            & CanAutomate('thruster-fuel', surface) & CanAutomate('thruster-oxidizer', surface)
            # Pipes are needed to transport propellants
            & CanCraft('pipe', surface) & CanCraft('pipe-to-ground', surface)
            # Pumps and storage tanks allow thruster throttling
            & CanCraft('pump', surface) & CanCraft('storage-tank', surface)
    )

    events = base_get_events(surface)

    events['Reach fulgora'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    events['Reach gleba'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    events['Reach vulcanus'] &= can_destroy_medium_asterorid & has_truster_and_propellants
    events['Reach aquilo'] &= can_destroy_big_asterorid & has_truster_and_propellants
    events['Reach solar-system-edge'] &= can_destroy_huge_asterorid & has_truster_and_propellants & has_non_solar_power
    events['Reach shattered-planet'] &= can_destroy_huge_asterorid & has_truster_and_propellants & has_non_solar_power

    return events
