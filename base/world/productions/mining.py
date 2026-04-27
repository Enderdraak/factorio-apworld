from rule_builder.rules import Rule, True_

from ...data.classes import Surface
from ...data.lookup import machines_by
from ...data.raw import machines_for_manual_craft
from ..rules import Any, CanAutomate, CanCraft, UnlockedMiningWithFluid

def get_mining_productions(surface: Surface) -> dict[str, tuple[Rule, dict[str, bool]]]:
    events = {}

    for resource in surface.resources:
        match (resource):
            case PumpableResource(name=name, fluid=fluid):
                machines = machines_by(can_be_placed_on=surface, is_offshore_pump=True)
                if len(machines) > 0:
                    events[f'Pump {name}'] = (
                        Any([CanCraft(machine.name, surface) for machine in machines]),
                        {fluid: True},
                    )

            case GatherableResource(name=name, results=results):
                events[f'Gather {name}'] = (
                    True_(),
                    {result: False for result in results},
                )

            case MinableResource(name=name, category=category, results=results, mining_fluid=mining_fluid):
                machines = machines_by(can_be_placed_on=surface, mining_category=category)

                if mining_fluid is None and len(machines_for_manual_craft.intersection((machine.name for machine in machines))) > 0:
                    events[f'Mine {name}'] = (
                        True_(),
                        {result: False for result in results},
                    )

                if len(machines) > 0:
                    rule = Any([CanCraft(machine.name, surface) for machine in machines])
                    if mining_fluid is not None:
                        rule &= UnlockedMiningWithFluid() & CanAutomate(mining_fluid, surface)
                    events[f'Automate {name} mining'] = (
                        rule,
                        {result: True for result in results},
                    )

    return events
